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

    print(f"Fetching and reconstructing sentences for pdfId {pdf_id}...")
    sentences_dict = ReadSentencesFromDb.reconstructSinglePdfSentences(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        table=sentence_table,
        pdfId=pdf_id
    )

    if not sentences_dict:
        print("No sentences retrieved. Exiting process.")
        return

    extractor = AllMiniLML6V2Extractor(model_path)

    truncated_ids = list(sentences_dict.keys())
    sentences_list = list(sentences_dict.values())

    print(f"Generating embeddings for {len(sentences_list)} sentences. This might take a moment...")
    embeddings_matrix = extractor.generate_embeddings(sentences_list)

    print("Connecting to database for insertion...")
    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()

        embeddingSqlColumnNames = os.getenv("EMBEDDING_COLUMNS")

        columns_list = [col.strip() for col in embeddingSqlColumnNames.split(',')]
        
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

            for vectorElementIndex, value in enumerate(embedding_vector):
                embeddingIndexOneBased  = vectorElementIndex + 1 
                normValue = value / vector_norm

                new_embedding_id = (truncated_text_id * 1000) + embeddingIndexOneBased
                
                batch_data.append((
                    new_embedding_id, 
                    embeddingIndexOneBased,    
                    float(normValue)   
                ))

                # Insert embeddings to MySql in batches
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