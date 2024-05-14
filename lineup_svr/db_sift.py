from db_maths import calculate_weighted_centroid
from elasticsearch import Elasticsearch
import env_dials
import json

db_conn = env_dials.db_conn
index_name = env_dials.index_name


def perform_search(search_query):
    """
        Handler for returning searches
    """
    try:
        # contact for search data
        response = env_dials.db_conn.search(index=env_dials.index_name, body=search_query)
        
        # return only data if found, drop search metadata
        return [hit['_source'] for hit in response['hits']['hits']]

    except Exception as e:
        print(f"Error during search: {str(e)}")
        # gracefully return nothing
        return []


def db_find_others(embedding):
    """
        higher level func for managing similar faces search
    """

    # main variables to change, range == 1..2
    primary_threshold = 1.788
    secondary_threshold = 1.644

    # make first query at primary threshold of similarity
    # only grab what is needed for average face calc (embeddings + facial_area)
    base_query = {
        'size': 100,
        'min_score': primary_threshold,
        'query': {
            'script_score': {
                'query': {'match_all': {}},
                'script': {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": embedding}
                }
            }
        },
        '_source': ['embedding', 'facial_area']
    }

    # get results
    primary_results = perform_search(base_query)

    # if len(results) == 0, return
    if len(primary_results) == 0:
        return

    # calculate average face from first results set
    weighted_avg_embedding = calculate_weighted_centroid(primary_results)

    # prepare secondary query with secondary threshold
    # drop embeddings from return, data slimming
    enhanced_query = {
        'size': 100,
        'min_score': secondary_threshold,
        'query': {
            'script_score': {
                'query': {'match_all': {}},
                'script': {
                    'source': 'cosineSimilarity(params.query_vector, "embedding") + 1.0',
                    'params': {'query_vector': weighted_avg_embedding.tolist()}
                }
            }
        },
        '_source': {"excludes": ["embedding"]}
    }

    # get secondary results
    secondary_results = perform_search(enhanced_query)

    # FUTURE: insert additional steps here

    # return
    return secondary_results


def db_embed_check(query):
    """
        meta function for delegating similarity search
    """

    # find results
    cumulative_results = db_find_others(query['embedding'])

    # gracefail
    if cumulative_results == None:
        return

    # prepare in return dict
    results = {"query": cumulative_results}

    try:
        # cast to appropriate format
        json_results = json.dumps(results)

        return json_results

    except Exception as e:
        print(e)


def db_hit_rate(face_content):
    """
        meta function for delegating len(similar faces)
    """
    # prepare return array inside input parameter, under new key
    face_content['hit_rate'] = []

    # for each face
    for embedding in face_content['embeddings']:

        # find similar faces
        find_rate = db_find_others(embedding)

        if find_rate == None:
            # if none, return 1, as in "only one face like this"
            face_content['hit_rate'].append(1)
        else:
            # if similar faces found, return number of faces found in db
            # this is easiest for UI, despite 'maths of persuasion'
            face_content['hit_rate'].append(len(find_rate))

    return face_content


def db_pic_check(content, x_per=-1, y_per=-1):
    """
        finding function for picture, can take in exact pixel location if needed
    """

    # unpack variables needed for search
    imageDirectURL = content['imageDirectURL']
    imageData = content['imageData']

    # define search query for only url, lightweight search
    query = {
        "query": {
            "term": {"imageDirectURL": imageDirectURL}
        }
    }

    # get results
    response = env_dials.db_conn.search(index=env_dials.index_name, body=query)

    # unpack only data, dropping meta data
    hits = response['hits']['hits']

    # gracefail
    if len(hits) == 0:
        return None

    # filter only where image data is found
    filtered_hits = [hit for hit in hits if hit['_source']['imageData'] == imageData]

    # if none, gracefail
    if len(filtered_hits) == 0:
        return None

    # prepare dict for return data
    collated_data = {
        "hostPageURL": content['hostPageURL'],
        "imageDirectURL": content['imageDirectURL'],
        "imageData": content['imageData'],
        "facial_area": [],
        "embeddings": []
    }

    # aggregate embeddings and facial_area
    # this data is per-face, while other data == photo as whole
    for hit in filtered_hits:
        src = hit['_source']
        collated_data['facial_area'].append(src.get('facial_area'))
        collated_data['embeddings'].append(src.get('embedding'))  # Collect each embedding


    return collated_data
