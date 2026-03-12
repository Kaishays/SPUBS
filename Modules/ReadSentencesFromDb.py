import mysql.connector
from collections import defaultdict

def reconstruct_sentences(host, port, user, password, database, table):
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
            ORDER BY textId ASC
        """
        
        print(f"Fetching characters...")
        cur.execute(query)
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
    
   