import os
from dotenv import find_dotenv, load_dotenv
import sys
import time

# Make python aware of parent directories. 
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from ModelRuntime.AllMiniLML6V2Extractor import AllMiniLML6V2Extractor
from GetEmbeddingsFromDb import reconstruct_embeddings
from Modules import ReadSentencesFromDb 
from ComputeMostSimilarEmbeddings import get_top_k_similar_vectors
from NormalizedQuery import get_normalized_query_vector

def main():

    load_dotenv(find_dotenv())

    DB_CONFIG = {
        "host": os.getenv("DB_HOST"), 
        "port": int(os.getenv("DB_PORT")),   
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME")
    }

    # Pulling parameters from .env
    EMBEDDING_TABLE = os.getenv("EMBEDDING_TABLE")
    SENTENCE_TABLE = os.getenv("SENTENCE_TABLE")
    MODEL_PATH = os.getenv("MODEL_PATH")
    
    print("--- Initializing Semantic Search App ---")
    
    # 1. Load the Model (Once)
    try:
        extractor = AllMiniLML6V2Extractor(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # 2. Load Embeddings from DB into memory (Once)
    db_vectors = reconstruct_embeddings(
        **DB_CONFIG, 
        table=EMBEDDING_TABLE
    )
    
    if not db_vectors:
        print("No embeddings found. Please run embedding manager script first.")
        return

    # 3. Load Sentences from DB (Once)
    sentences_text_map = ReadSentencesFromDb.reconstruct_sentences(
        **DB_CONFIG, 
        table=SENTENCE_TABLE
    )

    print("\nInitialization Complete. System is ready.")
    print("Type 'exit' or 'quit' to close the app.\n")


    # --- MAIN LOOP ---
    while True:
        user_query = input("\nEnter search phrase: ").strip()
        
        if user_query.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        
        if not user_query:
            continue

        # Start the timer (measuring performance, excluding human typing time)
        start_time = time.perf_counter()

        # 4. Process Query
        # Turns text into a normalized 384-dimensional vector
        query_vector = get_normalized_query_vector(user_query, extractor)
        
        # 5. Compute Similarity
        # Finds the top 10 IDs based on dot product (cosine similarity)
        top_ids, top_scores = get_top_k_similar_vectors(
            query_vector=query_vector, 
            embeddings_dict=db_vectors, 
            k=5
        )
        
        # 6. Display Results
        print(f"\nResults for: '{user_query}'")
        print("-" * 50)
        
        for i, (text_id, score) in enumerate(zip(top_ids, top_scores), 1):
            # Retrieve the sentence text using the ID
            sentence_text = sentences_text_map.get(text_id, "[Text not found in DB]")
            
            print(f"{i}. [Score: {score:.4f}] (ID: {text_id})")
            print(f"   {sentence_text}\n")

        # Stop the timer and convert seconds to milliseconds
        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000
        
        print(f"⏱️  Search completed in {elapsed_ms:.2f} ms")

if __name__ == "__main__":
    main()