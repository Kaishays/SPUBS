import numpy as np

def get_normalized_query_vector(query_text, extractor):
   
    raw_vector = extractor.generate_embeddings([query_text])[0]
    
    query_vector = np.array(raw_vector, dtype=np.float32)
    
    query_norm = np.linalg.norm(query_vector)
    
    if query_norm > 0:
        normalized_vector = query_vector / query_norm
    else:
        normalized_vector = query_vector
        
    return normalized_vector