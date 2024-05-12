from db_maths import calculate_weighted_centroid
from elasticsearch import Elasticsearch
import env_dials
import json

db_conn = env_dials.db_conn
index_name = env_dials.index_name


def perform_search(search_query):
    """Perform a search query on the Elasticsearch database."""

    try:
        response = env_dials.db_conn.search(index=env_dials.index_name, body=search_query)
        return [hit['_source'] for hit in response['hits']['hits']]
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return []

def db_find_others(embedding):
    primary_threshold = 1.788  # Adjusted cosine similarity threshold
    secondary_threshold = 1.644 # Adjusted cosine similarity threshold

    # Query for primary search
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

    # Perform primary search
    primary_results = perform_search(base_query)

    # Calculate weighted centroid of primary results
    if len(primary_results) == 0:
        return


    weighted_avg_embedding = calculate_weighted_centroid(primary_results)

    # Query for secondary search using the weighted average embedding
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

    # Perform secondary search
    secondary_results = perform_search(enhanced_query)

    return secondary_results


def db_embed_check(query):

    cumulative_results = db_find_others(query['embedding'])

    if cumulative_results == None:
        return

    results = {"query": cumulative_results}

    try:
        # Convert results to JSON string for transmission or logging
        json_results = json.dumps(results)
        return json_results
    except Exception as e:
        print(e)


def db_hit_rate(face_content):

    face_content['hit_rate'] = []

    for embedding in face_content['embeddings']:

        find_rate = db_find_others(embedding)

        if find_rate == None:
            face_content['hit_rate'].append(1)
        else:
            face_content['hit_rate'].append(len(find_rate))

    
    return face_content


def db_pic_check(content, x_per=-1, y_per=-1):

    imageDirectURL = content['imageDirectURL']
    imageData = content['imageData']

    # Define the search query to filter by imageDirectURL
    query = {
        "query": {
            "term": {"imageDirectURL": imageDirectURL}
        }
    }

    # Execute the search
    response = env_dials.db_conn.search(index=env_dials.index_name, body=query)
    hits = response['hits']['hits']

    if len(hits) == 0:
        return None

    # Filter hits where imageData matches
    filtered_hits = [hit for hit in hits if hit['_source']['imageData'] == imageData]

    if len(filtered_hits) == 0:
        return None  # Return None if no matching hits

    # Initialise a structure to hold the collated data
    collated_data = {
        "hostPageURL": content['hostPageURL'],
        "imageDirectURL": content['imageDirectURL'],
        "imageData": content['imageData'],
        "facial_area": [],
        "embeddings": []
    }

    # Iterate over the filtered hits to aggregate facial_area data and embeddings
    for hit in filtered_hits:
        src = hit['_source']
        collated_data['facial_area'].append(src.get('facial_area'))
        collated_data['embeddings'].append(src.get('embedding'))  # Collect each embedding

    return collated_data



