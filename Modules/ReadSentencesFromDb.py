from dotenv import load_dotenv
import mysql.connector
from collections import defaultdict
import os

load_dotenv()

def reconstructAllSentences(host, port, user, password, database, table):

    try:
        conn = mysql.connector.connect(
            host=host, 
            port=port, 
            user=user, 
            password=password, 
            database=database
        )
        cur = conn.cursor()


        columns_env = os.getenv("SENTENCE_COLUMNS")
        columns_list = [col.strip() for col in columns_env.split(',')]
        
       
        id_col = columns_list[0] 
        char_col = columns_list[4] 

        query = f"""
            SELECT `{id_col}`, `{char_col}`
            FROM `{table}`
            ORDER BY `{id_col}` ASC
        """
        
        print(f"Fetching characters...")
        cur.execute(query)
        rows = cur.fetchall()

        reconstructed_sentences = defaultdict(str)

        for row in rows:
            textId = row[0]
            charElement = row[1]

            # Define truncatedTextId by truncating by a factor of 1000
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
    

def reconstructSinglePdfSentences(host, port, user, password, database, table, pdfId):

    try:
        conn = mysql.connector.connect(
            host=host, 
            port=port, 
            user=user, 
            password=password, 
            database=database
        )
        cur = conn.cursor()

        columns_env = os.getenv("SENTENCE_COLUMNS")
        columns_list = [col.strip() for col in columns_env.split(',')]
        
        id_col = columns_list[0] 
        char_col = columns_list[4] 
        pdf_id_col = columns_list[1] 

        query = f"""
            SELECT `{id_col}`, `{char_col}`
            FROM `{table}`
            WHERE `{pdf_id_col}` = %s
            ORDER BY `{id_col}` ASC
        """
        
        print(f"Fetching characters for pdfId {pdfId}...")
        cur.execute(query, (pdfId,))
        rows = cur.fetchall()

        reconstructed_sentences = defaultdict(str)

        for row in rows:
            textId = row[0]
            charElement = row[1]

            # Define truncatedTextId by truncating by a factor of 1000
            truncatedTextId = textId // 1000

            # Append each char item to the string to make up the sentence
            reconstructed_sentences[truncatedTextId] += charElement

        print(f"Successfully reconstructed {len(reconstructed_sentences)} sentences for pdfId {pdfId}.")

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

   