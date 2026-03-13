import numpy as np

def get_top_k_similar_vectors(query_vector, embeddings_dict, k=10):
   
    results = []

    print(f"Calculating dot products against {len(embeddings_dict)} vectors...")
    
    for truncated_text_id, db_vector in embeddings_dict.items():
        
        if (len(db_vector) != len(query_vector) ):
            print(f"Warning: Dimension mismatch for ID {truncated_text_id}. Skipping.")
            continue

        db_norm = np.linalg.norm(db_vector)
        if db_norm > 0:
            db_vector_normalized = db_vector / db_norm
        else:
            db_vector_normalized = db_vector
            
        dot_product_score = np.dot(query_vector, db_vector_normalized)
        
        results.append((dot_product_score, truncated_text_id))
        
    results.sort(key=lambda x: x[0], reverse=True)
    
    top_k_ids = [item[1] for item in results[:k]]
    top_k_scores = [item[0] for item in results[:k]] 
    
    return top_k_ids, top_k_scores