from elasticsearch import Elasticsearch
import env_dials
from functools import partial

db_conn = env_dials.db_conn
index_name = env_dials.index_name

def db_del_all():
    """
        reset database
    """

    # define match all query
    query = {
    "query": {
        "match_all": {}
    }
    }

    # match all & delete
    response = db_conn.delete_by_query(index=index_name,
                                                body=query,
                                                conflicts='proceed')

    # print records
    print(response)


def db_mapping_update():
    """
        apply update to schema
    """

    # define new schema (wanted schema)
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
        # attempt update
        db_conn.options(ignore_status=400).indices.create(index=index_name, body=index_settings)

    except:
        # silent failure, allows for update attempt to only succeed when db == new
        pass



def index_document(document, index, conn):
    """
        portable task for handling document input into db
    """
    
    # attempt to index new document
    try:
        response = conn.index(index=index, document=document)

        print(f"db added face")
        return f"Document added to {index}, ID: {response['_id']}"

    except Exception as e:
        print(f"err, index_document: db failed to add: {str(e)}")
        return f"Failed to add document to {index}: {str(e)}"


def db_face_add(content, index_name, db_conn):
    """
        meta function for creating portable tasks, to be executed

        FUTURE: update this and app.face_req for better separation of concerns
    """
    
    # return array
    tasks = []

    # validate data via len(embeddings) == len(facial_area)
    for i in range(len(content['embeddings'])):

        # prep information into db format
        # aka embedding NOT embeddingS
        data_point = {
            "hostPageURL": content['hostPageURL'],
            "imageDirectURL": content['imageDirectURL'],
            "imageData": content['imageData'],
            "facial_area": content['facial_area'][i],
            "embedding": content['embeddings'][i]
        }

        # create portable task, to be fed into partial
        task = partial(index_document,
                    document=data_point,
                    index=index_name,
                    conn=db_conn)
        
        # add to queue
        tasks.append(task)

    # return task
    return tasks
