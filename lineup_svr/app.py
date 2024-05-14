import asyncio
from concurrent.futures import ThreadPoolExecutor
from data_parse import post_analysis
from deepface import DeepFace
import db_sift
import db_mgmt
import env_dials
import json
import websockets

# adjust as necessary for localhost
executor = ThreadPoolExecutor(max_workers=4)

async def lifo_task_executor(task_stack):
    """
        takes in a LIFO queue and executes
    """

    while task_stack:
        # remove last item on queue
        func, args, response_stack = task_stack.pop()

        # start processing
        result = await asyncio.get_running_loop().run_in_executor(executor, func, *args)

        # place result in results queue
        response_stack.append(result)

async def response_handler(response_stack, websocket):
    """
        takes in a LIFO queue and responds to websocket
    """

    while response_stack:
        
        # remove last result on queue
        response = response_stack.pop()

        # validate response
        if response:

            # attempt transmission
            try:
                await websocket.send(response)

            except Exception as e:
                print('Error in handle_client, post analysis:', e)


async def manage_tasks_and_responses(task_stack, response_stack, websocket):
    """
        meta function to delegate dual queue (operation & results queues)
    """

    # implement operation queue future
    task_future = asyncio.create_task(lifo_task_executor(task_stack))

    # implement results queue future
    response_future = asyncio.create_task(response_handler(response_stack, websocket))

    # align queues
    await asyncio.gather(task_future, response_future)

    

def face_req(img_content):
    """
        primary operation function for images
    """

    # attempt to return from database
    db_returns = db_sift.db_pic_check(img_content)

    if db_returns:

        # append latest 'hit_rate' from database
        db_returns = db_sift.db_hit_rate(db_returns)
        print('returning from db')

        # return in appropriate format
        return json.dumps(db_returns)

    else:

        # fresh data to unpack and store
        img_path = img_content['imageData']

        # use deepface to handle image restructuring/resizing for model
        try:
            results = DeepFace.represent(img_path=img_path,
                                        model_name='Facenet512',
                                        detector_backend='mtcnn',
                                        enforce_detection=False)

            # remove results if less than 80% sure there was a face
            high_conf_results = [result for result in results if result['face_confidence'] > 0.8]

            # unpack analysis of model result
            faces, embeddings = post_analysis(high_conf_results, img_path)

            # remove old dict key and values
            img_content.pop('facial_area', None)

            # append analysis dict key and values
            img_content['facial_area'] = faces
            img_content['embeddings'] = embeddings

            # for each face found, create a storage task
            tasks = db_mgmt.db_face_add(img_content,
                                        env_dials.index_name,
                                        env_dials.db_conn)

            # send each task to operation queue
            for task in tasks:
                executor.submit(task)

            # append latest 'hit_rate' from database
            img_content = db_sift.db_hit_rate(img_content)

            # trim message size before sending
            img_content.pop('imageData', None)

            # return in appropriate format
            return json.dumps(img_content)

        except Exception as e:
            # print error with tracable datapoint
            print(f'err, face_req: {e}')
            print(img_content)

    # returns nothing if no faces found
    return []


async def handle_client(websocket, path):
    """
        switchboard for incoming
    """

    # holding arrays for multithreaded queues
    task_stack = []
    response_stack = []

    # inspect message to divert
    async for message in websocket:
        
        # cast to json
        try:
            message_data = json.loads(message)
        except Exception as e:
            print('err, handle_client: json conversion failed')

            # if triggered automatically, to get image data
        if 'content' in message_data:
            
            # add to operation queue, to check for recognition
            task_stack.append((face_req,
                                (message_data['content'],),
                                response_stack))

            # if triggered by user action, to query iamge data
        elif 'query' in message_data:

            # add to operation queue, to check for similar faces
            task_stack.append((db_sift.db_embed_check,
                                (message_data['query'],),
                                response_stack))
        
        if task_stack:
            
            # if anything was added to operation queue
            # process in LIFO
            await lifo_task_executor(task_stack)
        
        if response_stack:
            # if anything was added to results queue
            # process in LIFO
            await response_handler(response_stack, websocket)


async def main():
    """
        main running function
    """

    # config server options with no timeout, no ping, large image size
    server = await websockets.serve(handle_client,
                                    'localhost',
                                    2882,
                                    max_size=50**7,
                                    ping_interval=None,
                                    open_timeout=None,
                                    close_timeout=None)

    print('WebSocket server started on ws://localhost:2882')

    # run forever
    await server.wait_closed()


if __name__=='__main__':
    # apply update to schema if needed
    db_mgmt.db_mapping_update()

    # start the main running function
    asyncio.run(main())
