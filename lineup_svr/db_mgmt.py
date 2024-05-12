from elasticsearch import Elasticsearch
import env_dials
from functools import partial

db_conn = env_dials.db_conn
index_name = env_dials.index_name

def db_del_all():
    # Connect to the local Elasticsearch instance
    # Define the query to match all documents
    query = {
    "query": {
        "match_all": {}
    }
    }

    # Perform the delete by query operation
    response = db_conn.delete_by_query(index=index_name,
                                                body=query,
                                                conflicts='proceed')

    # Print the response to see the result of the delete operation
    print(response)

def db_mapping_update():

    # Define the new settings and mappings for the index
    index_settings = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            }
        },
        "mappings": {
            "properties": {
                "embedding": {
                    "type": "dense_vector",
                    "dims": 512
                },
                "imageData": {
                    "type": "text",
                    "index": False
                },
                "hostPageURL": {
                    "type": "keyword"
                },
                "imageDirectURL": {
                    "type": "keyword"
                },
                "facial_area": {
                    "type": "object",
                    "properties": {
                        "x": {
                            "type": "integer"
                        },
                        "y": {
                            "type": "integer"
                        },
                        "w": {
                            "type": "integer"
                        },
                        "h": {
                            "type": "integer"
                        },
                        "x_per": {
                            "type": "float"
                        },
                        "y_per": {
                            "type": "float"
                        }
                    }
                }
            }
        }
    }    
    
    try:
        # Create the new index with the specified settings and mappings
        db_conn.options(ignore_status=400).indices.create(index=index_name, body=index_settings)

    except:
        pass



def index_document(document, index, conn):
    try:
        response = conn.index(index=index, document=document)
        print(f"db added face")
        return f"Document added to {index}, ID: {response['_id']}"
    except Exception as e:
        print(f"err, index_document: db failed to add: {str(e)}")
        return f"Failed to add document to {index}: {str(e)}"


def db_face_add(content, index_name, db_conn):

    tasks = []

    # Ensure embeddings and facial_area are indexed similarly
    for i in range(len(content['embeddings'])):
        # Prepare the document to be indexed
        data_point = {
            "hostPageURL": content['hostPageURL'],
            "imageDirectURL": content['imageDirectURL'],
            "imageData": content['imageData'],
            "facial_area": content['facial_area'][i],
            "embedding": content['embeddings'][i]
        }

        # Create a callable task using partial
        task = partial(index_document,
                    document=data_point,
                    index=index_name,
                    conn=db_conn)
        
        tasks.append(task)

    return tasks