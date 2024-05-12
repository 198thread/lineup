import base64
from io import BytesIO
from PIL import Image
from deepface import DeepFace

def post_analysis(results, img_data):

    face_embeddings = []
    facial_data = []

    for face in results:

        facial_area = face['facial_area']
        embedding = face['embedding']

        try:
            # Decode the base64 string
            mimeless_image = img_data.split('base64,')[1]
            image_data = base64.b64decode(mimeless_image)
            
            # Open the image using PIL
            image = Image.open(BytesIO(image_data))
            
            # Get dimensions
            width, height = image.size

            centre_x = facial_area['x'] + (facial_area['w'] / 1.2)
            centre_y = facial_area['y'] + (facial_area['h'] / 20)

            facial_returns = {
                'x': facial_area['x'],
                'y': facial_area['y'],
                'h': facial_area['h'],
                'w': facial_area['w'],
                'x_per': (centre_x / width) * 100,
                'y_per': (centre_y / height) * 100
            }

            facial_data.append(facial_returns)
            face_embeddings.append(embedding)

        except Exception as e:
            print(f'Error in post_analysis: {e}')

    return facial_data, face_embeddings

