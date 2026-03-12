import numpy as np

def get_top_k_similar_vectors(query_vector, embeddings_dict, k=10):
    """
    Computes the dot product between a normalized query vector and all vectors 
    in the database dictionary. 
    
    Returns:
        A list of the top k truncatedTextIds with the highest dot products.
    """
    results = []

    print(f"Calculating dot products against {len(embeddings_dict)} vectors...")
    
    # Iterate through all database vectors
    for truncated_text_id, db_vector in embeddings_dict.items():
        
        # Normalize the database vector (if it wasn't normalized before insertion)
        db_norm = np.linalg.norm(db_vector)
        if db_norm > 0:
            db_vector_normalized = db_vector / db_norm
        else:
            db_vector_normalized = db_vector
            
        # Compute the dot product (Cosine Similarity)
        dot_product_score = np.dot(query_vector, db_vector_normalized)
        
        # Store the score and its corresponding ID
        results.append((dot_product_score, truncated_text_id))
        
    # Sort the results by score in descending order (highest score first)
    results.sort(key=lambda x: x[0], reverse=True)
    
    # Extract just the top k IDs
    top_k_ids = [item[1] for item in results[:k]]
    top_k_scores = [item[0] for item in results[:k]] # Keeping scores for display
    
    return top_k_ids, top_k_scores