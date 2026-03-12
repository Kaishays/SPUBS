import mysql.connector
import numpy as np
from collections import defaultdict

def reconstruct_embeddings(host, port, user, password, database, table):
    """
    Connects to the database, fetches all individual embedding elements,
    and reconstructs the full 384-dimensional vectors.
    
    Returns a dictionary:
    { truncatedTextId (int): embedding_vector (numpy array) }
    """
    print(f"Connecting to database to fetch embeddings from `{table}`...")
    
    try:
        conn = mysql.connector.connect(
            host=host, 
            port=port, 
            user=user, 
            password=password, 
            database=database
        )
        cur = conn.cursor()

        # By ordering by embeddingId ASC, we guarantee that the vector elements
        # (index 0 to 383) are retrieved and appended in the exact correct order.
        query = f"""
            SELECT embeddingId, embeddingElementNormalized
            FROM `{table}`
            ORDER BY embeddingId ASC
        """
        
        print("Executing query (this might take a moment depending on table size)...")
        cur.execute(query)

        # Using a defaultdict to gather the 384 floats for each sentence
        embeddings_dict = defaultdict(list)
        
        print("Fetching rows and reconstructing vectors...")
        
        # Fetching in chunks to prevent memory overflow if the table is massive
        chunk_size = 100000 
        while True:
            rows = cur.fetchmany(chunk_size)
            if not rows:
                break # Exit the loop when no more rows are returned
                
            for row in rows:
                embedding_id = row[0]
                embedding_element = row[1]
                
                # Derive the parent truncatedEmbeddingId by reversing our previous math
                truncated_embedding_id = embedding_id // 1000
                
                # Append the float to the sentence's vector list
                embeddings_dict[truncated_embedding_id].append(embedding_element)

        # Convert standard Python lists to numpy arrays for semantic search operations
        print("Converting reconstructed lists to numpy arrays...")
        final_dict = {
            key: np.array(vector, dtype=np.float32) 
            for key, vector in embeddings_dict.items()
        }
        
        print(f"Successfully reconstructed {len(final_dict)} embedding vectors.")
        return final_dict

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}
    finally:
        # Always ensure connections are closed safely
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# ==========================================
# Example Usage / Quick Test
# ==========================================
if __name__ == "__main__":
    DB_CONFIG = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "132312ADADADAqeqeqeqe#!#!#!#!!#!KJLKJ",
        "database": "harry_potter_semantics"
    }
    
    # Using the table name from your previous DELETE snippet
    TABLE_NAME = "all-minilm-l6-v2"
    
    vectors_dict = reconstruct_embeddings(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        table=TABLE_NAME
    )
    
    # Quick verification test
    if vectors_dict:
        # Grab the first key-value pair to inspect it
        sample_key = next(iter(vectors_dict))
        sample_vector = vectors_dict[sample_key]
        
        print(f"\n--- Verification ---")
        print(f"Sample truncatedTextId: {sample_key}")
        print(f"Vector dimensions: {len(sample_vector)} (Should be 384)")
        print(f"Vector data type: {type(sample_vector)}")
        print(f"First 5 elements: {sample_vector[:5]}")