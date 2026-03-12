import mysql.connector
from collections import defaultdict

def reconstruct_sentences(host, port, user, password, database, table, bookId):
    """
    Connects to the database, fetches characters for a specific book, 
    and reconstructs the original sentences.
    """
    try:
        # 1. Connect to the database
        conn = mysql.connector.connect(
            host=host, 
            port=port, 
            user=user, 
            password=password, 
            database=database
        )
        cur = conn.cursor()

        # 2. Query the characters
        query = f"""
            SELECT textId, charElement
            FROM `{table}`
            WHERE bookID = %s
            ORDER BY textId ASC
        """
        
        print(f"Fetching characters for bookId {bookId}...")
        cur.execute(query, (bookId,))
        rows = cur.fetchall()

        # We will use a defaultdict initialized with empty strings to append characters
        reconstructed_sentences = defaultdict(str)

        # 3. Iterate the query array
        for row in rows:
            textId = row[0]
            charElement = row[1]

            # Define truncatedTextId by truncating by a factor of 1000
            # Using integer division (//) drops the decimals automatically
            truncatedTextId = textId // 1000

            # Append each char item to the string to make up the sentence
            reconstructed_sentences[truncatedTextId] += charElement

        print(f"Successfully reconstructed {len(reconstructed_sentences)} sentences.")

         # Iterate through the unique values of embeddingIndex
        for sentence in reconstructed_sentences.values():
            print(sentence)

        for sentence in reconstructed_sentences:
            print(sentence)
        
        return reconstructed_sentences

    except Exception as e:
        print(f"An error occurred: {e}")
        return {}
        
    finally:
        # Always ensure connections are closed
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# ==========================================
# Example Usage
# ==========================================
if __name__ == "__main__":
    # Replace these with your actual database credentials
    DB_HOST = "localhost"
    DB_PORT = 3306
    DB_USER = "root"
    DB_PASSWORD = "132312ADADADAqeqeqeqe#!#!#!#!!#!KJLKJ"
    DB_NAME = "harry_potter_semantics"
    TABLE_NAME = "harrypottersentences"
    TARGET_BOOK_ID = 7  # The bookId you want to reconstruct

    sentences_dict = reconstruct_sentences(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        table=TABLE_NAME,
        bookId=TARGET_BOOK_ID
    )

    # Print out the first 5 reconstructed sentences to verify
    print("\n--- Sample Output ---")
    
   