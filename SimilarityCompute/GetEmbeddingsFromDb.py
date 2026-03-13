import os
from dotenv import load_dotenv
import mysql.connector
import numpy as np
from collections import defaultdict

load_dotenv()

def reconstruct_embeddings(host, port, user, password, database, table):
    
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

        columns_env = os.getenv("EMBEDDING_COLUMNS")
        columns_list = [col.strip() for col in columns_env.split(',')]
        id_col = columns_list[0]      
        element_col = columns_list[2]
        
        query = f"""
            SELECT `{id_col}`, `{element_col}`
            FROM `{table}`
            ORDER BY `{id_col}` ASC
        """
        
        print("Executing query (this might take a moment depending on table size)...")
        cur.execute(query)

        embeddings_dict = defaultdict(list)
        
        print("Fetching rows and reconstructing vectors...")
        
        # Fetching in chunks to prevent memory overflow 
        chunk_size = 100000 
        while True:
            rows = cur.fetchmany(chunk_size)
            if not rows:
                break 
                
            for row in rows:
                embedding_id = row[0]
                embedding_element = row[1]
                
                truncated_embedding_id = embedding_id // 1000
                
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
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()