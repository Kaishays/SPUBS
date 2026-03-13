import os
import mysql.connector
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

def insert_sentences(sentences, host, port, user, password, database, table, pdfId, log_path):
    if not sentences:
        return

    conn = mysql.connector.connect(host=host, port=port, user=user, password=password, database=database)
    cur = conn.cursor()
    
    columns_env = os.getenv("SENTENCE_COLUMNS")
    
    columns_list = [col.strip() for col in columns_env.split(',')]
    formatted_columns = ", ".join([f"`{col}`" for col in columns_list])
    
    insert_sql = f"INSERT INTO `{table}` ({formatted_columns}) VALUES (%s, %s, %s, %s, %s)"

    try:
        bookIdFactor = 100_000_000
        sentenceIndexFactor = 1_000
        maxEmbeddingSize = 800
        
        with open(log_path, "a", encoding="utf-8") as f:
            
            sentenceIndex = 1
            for sentence in sentences:
                if not sentence:
                    continue

                if (sentenceIndex == 4):
                    print(f"Debug: Processing sentence {sentenceIndex} with length {len(sentence)}")
                    print(f"Content: {sentence[:100]}...")  # Print the first 100 characters for context

                if len(sentence) > maxEmbeddingSize:
                    f.write(f"Index: {sentenceIndex} | Length: {len(sentence)}\n")
                    f.write(f"Content: {sentence}\n")
                    f.write("-" * 50 + "\n")
                    continue

                char_data = [] 
                charIndex = 1
                
                # 3. Loop through characters
                for char in sentence:

                    textId = (pdfId * bookIdFactor) + (sentenceIndex * sentenceIndexFactor) + charIndex
                    print(charIndex)
                    char_data.append((textId, sentenceIndex, pdfId, charIndex, char))
                    charIndex += 1

                # Insert the whole sentence's characters in one batch
                if char_data:
                    cur.executemany(insert_sql, char_data)
                
                sentenceIndex += 1
                
        # Commit once at the very end for maximum speed
        conn.commit()
        # Changed to -1 so it prints the actual number of completed sentences
        print(f"Successfully imported {sentenceIndex - 1} sentences.")

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()