import sys
import os
from dotenv import find_dotenv, load_dotenv
import numpy as np 

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import mysql.connector
from Modules import ReadSentencesFromDb
from ModelRuntime.AllMiniLML6V2Extractor import AllMiniLML6V2Extractor

def process_and_store_embeddings(db_config, sentence_table, embedding_table, pdf_id, model_path):
    # 1. Reconstruct sentences from the database using ReadSentencesFromDb
    print(f"Fetching and reconstructing sentences for bookId {pdf_id}...")
    sentences_dict = ReadSentencesFromDb.reconstruct_sentences(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        table=sentence_table,
        bookId=pdf_id
    )

    if not sentences_dict:
        print("No sentences retrieved. Exiting process.")
        return

    # 2. Initialize the Extractor Manager using the new class
    extractor = AllMiniLML6V2Extractor(model_path)

    # 3. Extract IDs and sentences into aligned lists for batch processing
    truncated_ids = list(sentences_dict.keys())
    sentences_list = list(sentences_dict.values())

    # 4. Generate embeddings in a single batch (highly optimized)
    print(f"Generating embeddings for {len(sentences_list)} sentences. This might take a moment...")
    embeddings_matrix = extractor.generate_embeddings(sentences_list)

    # 5. Connect to DB and insert the results
    print("Connecting to database for insertion...")
    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()

        columns_env = os.getenv("EMBEDDING_COLUMNS", "embeddingId,embeddingIndex,embeddingElementNormalized")
        columns_list = [col.strip() for col in columns_env.split(',')]
        
        formatted_columns = ", ".join([f"`{col}`" for col in columns_list])
        
        insert_query = f"INSERT INTO `{embedding_table}` ({formatted_columns}) VALUES (%s, %s, %s)"
        
        batch_data = []
        batch_size = 5000 # Batch inserts to avoid MySQL packet/memory limits
        
        # Iterate over the aligned IDs and their newly generated embedding vectors
        for truncated_text_id, embedding_vector in zip(truncated_ids, embeddings_matrix):
            
            # Calculate the L2 norm (magnitude) of the vector
            vector_norm = np.linalg.norm(embedding_vector)
            
            if vector_norm <= 0:
               vector_norm = 1e-10 

            for vector_index, value in enumerate(embedding_vector):
                vector_index_oneBased  = vector_index + 1 
                normValue = value / vector_norm

                # Compute absolute unique ID (truncatedTextId * 1000 + the 0-383 vector index)
                new_embedding_id = (truncated_text_id * 1000) + vector_index_oneBased
                
                batch_data.append((
                    new_embedding_id, 
                    vector_index_oneBased,    # Maps to your 'embeddingIndex' (smallint unsigned)
                    float(normValue)     # Maps to your 'embeddingElement' (float)
                ))

                # Insert in batches
                if len(batch_data) >= batch_size:
                    cur.executemany(insert_query, batch_data)
                    conn.commit()
                    batch_data = [] 

        # Insert final leftover batch
        if batch_data:
            cur.executemany(insert_query, batch_data)
            conn.commit()

        print("Successfully processed and stored all embedding vectors!")

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    load_dotenv(find_dotenv())

    DB_CONFIG = {
        "host": os.getenv("DB_HOST"), 
        "port": int(os.getenv("DB_PORT")),   
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME")
    }
    
    SENTENCE_TABLE = os.getenv("SENTENCE_TABLE")
    EMBEDDING_TABLE = os.getenv("EMBEDDING_TABLE")
    TARGET_PDF_ID = int(os.getenv("TARGET_PDF_ID"))
    MODEL_PATH = os.getenv("MODEL_PATH")

    process_and_store_embeddings(
        db_config=DB_CONFIG,
        sentence_table=SENTENCE_TABLE,
        embedding_table=EMBEDDING_TABLE,
        pdf_id=TARGET_PDF_ID,
        model_path=MODEL_PATH
    )