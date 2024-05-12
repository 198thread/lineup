import asyncio
from deepface import DeepFace
import db_sift
import db_mgmt
import env_dials
import json
import websockets
from concurrent.futures import ThreadPoolExecutor
from data_parse import post_analysis

executor = ThreadPoolExecutor(max_workers=4)

async def lifo_task_executor(task_stack):
    while task_stack:
        func, args, response_stack = task_stack.pop()
        result = await asyncio.get_running_loop().run_in_executor(executor, func, *args)
        response_stack.append(result)

async def response_handler(response_stack, websocket):
    while response_stack:
        response = response_stack.pop()
        if response:
            try:
                await websocket.send(response)
            except Exception as e:
                print('Error in handle_client, post analysis:', e)

async def manage_tasks_and_responses(task_stack, response_stack, websocket):

    task_future = asyncio.create_task(lifo_task_executor(task_stack))

    response_future = asyncio.create_task(response_handler(response_stack, websocket))

    await asyncio.gather(task_future, response_future)

    

def face_req(img_content):

    db_returns = db_sift.db_pic_check(img_content)

    if db_returns:

        db_returns = db_sift.db_hit_rate(db_returns)
        print('returning from db')

        return json.dumps(db_returns)

    else:

        img_path = img_content['imageData']

        try:
            results = DeepFace.represent(img_path=img_path,
                                        model_name='Facenet512',
                                        detector_backend='mtcnn',
                                        enforce_detection=False)

            high_conf_results = [result for result in results if result['face_confidence'] > 0.8]

            faces, embeddings = post_analysis(high_conf_results, img_path)

            img_content.pop('facial_area', None)

            img_content['facial_area'] = faces
            img_content['embeddings'] = embeddings

            tasks = db_mgmt.db_face_add(img_content,
                                        env_dials.index_name,
                                        env_dials.db_conn)

            for task in tasks:
                executor.submit(task)

            img_content = db_sift.db_hit_rate(img_content)
            img_content.pop('imageData', None)

            return json.dumps(img_content)

        except Exception as e:
            print(f'err, face_req: {e}')
            print(img_content)

    return []


async def handle_client(websocket, path):
    task_stack = []
    response_stack = []

    async for message in websocket:
        try:
            message_data = json.loads(message)
        except Exception as e:
            print('err, handle_client: json conversion failed')

        if 'content' in message_data:
            # Append tasks to the stack with function, args, and where to store responses
            task_stack.append((face_req,
                                (message_data['content'],),
                                response_stack))
        elif 'query' in message_data:
            task_stack.append((db_sift.db_embed_check,
                                (message_data['query'],),
                                response_stack))
        
        # Trigger tasks execution in LIFO order
        if task_stack:
            await lifo_task_executor(task_stack)
        
        # Handle responses in LIFO order
        if response_stack:
            await response_handler(response_stack, websocket)


async def main():

    server = await websockets.serve(handle_client,
                                    'localhost',
                                    2882,
                                    max_size=50**7,
                                    ping_interval=None,
                                    open_timeout=None,
                                    close_timeout=None)

    print('WebSocket server started on ws://localhost:2882')
    await server.wait_closed()

db_mgmt.db_mapping_update()

asyncio.run(main())