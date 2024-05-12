import numpy as np

def calculate_weighted_centroid(results):
    # Ensure results is a list of dictionaries as expected
    if not all(isinstance(hit, dict) for hit in results):
        raise ValueError("Results should be a list of dictionaries.")
    
    # Prepare arrays directly if data is valid
    try:
        embeddings = np.array([hit['embedding'] for hit in results if 'embedding' in hit and len(hit['embedding']) == 512], dtype=np.float32)
        areas = np.array([(hit['facial_area']['w'], hit['facial_area']['h'])
                          for hit in results if 'facial_area' in hit and 'w' in hit['facial_area'] and 'h' in hit['facial_area']], dtype=np.float32)
    except KeyError as e:
        raise ValueError(f"Missing expected key in data: {e}")

    # Ensure all embeddings and facial areas are collected correctly
    if embeddings.shape[0] == 0 or areas.shape[0] == 0 or embeddings.shape[0] != areas.shape[0]:
        raise ValueError("Mismatch in the number of embeddings and facial areas, or missing data.")

    # Calculate weights from the widths and heights
    weights = areas[:, 0] * areas[:, 1]  # Multiply width by height

    # Calculate the weighted average using numpy's dot product for higher performance
    total_weight = np.sum(weights)
    if total_weight > 0:
        weighted_sum = np.dot(weights, embeddings) / total_weight
    else:
        # If total weight is zero, handle gracefully by returning an unmodified average or handle as a special case
        weighted_sum = np.mean(embeddings, axis=0)

    # Normalize the weighted average if the norm is non-zero
    norm = np.linalg.norm(weighted_sum)
    if norm == 0:
        return weighted_sum  # Return weighted average directly if norm is zero
    else:
        return weighted_sum / norm