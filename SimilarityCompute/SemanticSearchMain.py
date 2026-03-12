from ModelRuntime import AllMiniLML6V2Extractor 
from GetEmbeddingsFromDb import reconstruct_embeddings
from Modules import ReadSentencesFromDb 
from ComputeMostSimilarEmbeddings import get_top_k_similar_vectors
from NormalizedQuery import get_normalized_query_vector


def main():
    # --- CONFIGURATION ---
    DB_CONFIG = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "132312ADADADAqeqeqeqe#!#!#!#!!#!KJLKJ",
        "database": "harry_potter_semantics"
    }
    EMBEDDING_TABLE = "all-minilm-l6-v2"
    SENTENCE_TABLE = "harrypottersentences"
    MODEL_PATH = r'C:\Git\BERT\HP-Semantic Search\all-MiniLM-L6-v2'
    BOOK_ID = 7 # Adjust if you processed a different book
    
    print("--- Initializing Semantic Search App ---")
    
    # 1. Load the Model (Once)
    try:
        extractor = AllMiniLML6V2Extractor(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # 2. Load Embeddings from DB into memory (Once)
    # This allows for lightning-fast searching without DB overhead per query
    db_vectors = reconstruct_embeddings(
        **DB_CONFIG, 
        table=EMBEDDING_TABLE
    )
    
    if not db_vectors:
        print("No embeddings found. Please run your embedding manager script first.")
        return

    # 3. Load Sentences from DB (Once)
    # We need this to turn truncatedTextIds back into readable text
    sentences_text_map = ReadSentencesFromDb.reconstruct_sentences(
        **DB_CONFIG, 
        table=SENTENCE_TABLE, 
        bookId=BOOK_ID
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

if __name__ == "__main__":
    main()