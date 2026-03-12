import numpy as np

def get_normalized_query_vector(query_text, extractor):
    """
    Takes a string, generates its embedding, and returns a 
    normalized L2 numpy array.
    """
    # 1. Generate the raw embedding (returns a list of lists, we take the first)
    raw_vector = extractor.generate_embeddings([query_text])[0]
    
    # 2. Ensure it is a numpy array
    query_vector = np.array(raw_vector, dtype=np.float32)
    
    # 3. Perform L2 Normalization
    # This scales the vector so its magnitude is 1.0
    query_norm = np.linalg.norm(query_vector)
    
    if query_norm > 0:
        normalized_vector = query_vector / query_norm
    else:
        normalized_vector = query_vector
        
    return normalized_vector