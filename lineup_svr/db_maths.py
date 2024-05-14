import numpy as np

def calculate_weighted_centroid(results):
    """
    apply calculation to get average embedding, with largest face -> more weighting
    """

    # validate data from db
    if not all(isinstance(hit, dict) for hit in results):
        raise ValueError("Results should be a list of dictionaries.")
    
    # prepare into np.float32 arrays, pre-calc
    try:
        embeddings = np.array([hit['embedding'] for hit in results if 'embedding' in hit and len(hit['embedding']) == 512], dtype=np.float32)

        areas = np.array([(hit['facial_area']['w'], hit['facial_area']['h'])
                          for hit in results if 'facial_area' in hit and 'w' in hit['facial_area'] and 'h' in hit['facial_area']], dtype=np.float32)

    except KeyError as e:
        raise ValueError(f"Missing expected key in data: {e}")

    # validate after preparation
    if embeddings.shape[0] == 0 or areas.shape[0] == 0 or embeddings.shape[0] != areas.shape[0]:
        raise ValueError("Mismatch in the number of embeddings and facial areas, or missing data.")

    # calculate weights based on area of image, height . width
    weights = areas[:, 0] * areas[:, 1]

    # calculate total of weights
    total_weight = np.sum(weights)
    
    # if weights found...
    if total_weight > 0:
        
        # calcalate weights via sum, using np.dot
        weighted_sum = np.dot(weights, embeddings) / total_weight
    else:
        # if no weights, return averaged embeddings, without weighting
        weighted_sum = np.mean(embeddings, axis=0)

    # !normalise weighting. Incredibly important!
    norm = np.linalg.norm(weighted_sum)
    
    # if no norms found, return weighted sum
    if norm == 0:
        return weighted_sum
    else:
        # norm found, return normalised weighted sum, aka weighted centroid
        return weighted_sum / norm
