import base64
from deepface import DeepFace
from io import BytesIO
from PIL import Image

def post_analysis(results, img_data):
    """
        extract data into format for sending over socket
    """

    # holder variables, to be returned
    face_embeddings = []
    facial_data = []

    # only process if faces found
    for face in results:

        # unpack from model data
        facial_area = face['facial_area']
        embedding = face['embedding']

        try:
            # decode the base64 string
            mimeless_image = img_data.split('base64,')[1]
            image_data = base64.b64decode(mimeless_image)
            
            # open the image using PIL
            image = Image.open(BytesIO(image_data))
            
            # get dimensions
            width, height = image.size

            # calculate appropriate place for html button
            centre_x = facial_area['x'] + (facial_area['w'] / 1.2)
            centre_y = facial_area['y'] + (facial_area['h'] / 20)

            # pack location data into one dict
            facial_returns = {
                'x': facial_area['x'],
                'y': facial_area['y'],
                'h': facial_area['h'],
                'w': facial_area['w'],
                'x_per': (centre_x / width) * 100,
                'y_per': (centre_y / height) * 100
            }

            # add per-face data to return array
            facial_data.append(facial_returns)
            face_embeddings.append(embedding)

        except Exception as e:
            print(f'Error in post_analysis: {e}')

    return facial_data, face_embeddings
