import mysql.connector

def insert_sentences(sentences, host, port, user, password, database, table, pdfId):
    if not sentences:
        return

    conn = mysql.connector.connect(host=host, port=port, user=user, password=password, database=database)
    cur = conn.cursor()
    
    # We'll use a transaction to make this 100x faster
    insert_sql = (f"INSERT INTO `{table}` (`textId`, `sentenceIndex`, `pdfId`, `charIndex`, `charElement`)"
                  " VALUES (%s, %s, %s, %s, %s)")
    
    

    try:
        bookIdFactor = 100_000_000
        sentenceIndexFactor = 1_000
        maxEmbeddingSize = 800

        seen_ids = set()
        
        with open("C:\\Git\\BERT\\HP-Semantic Search\\long_sentences_log.txt", "a", encoding="utf-8") as f:
            
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
                #'But there is a cure in the house, and not outside it, no; not from others but from them, their bloody strife.'
                # We sing to you, dark gods beneath the earth.
                for char in sentence:

                    textId = (pdfId * bookIdFactor) + (sentenceIndex * sentenceIndexFactor) + charIndex
                    print(charIndex)
                    char_data.append((textId, sentenceIndex, pdfId, charIndex, char))
                    charIndex += 1

                    # 2. NEW: Check if this ID is already in our set
                    if textId in seen_ids:
                        print(f"🚨 DUPLICATE DETECTED! ID {textId} was already generated.")
                        print(f"   Occurred at Sentence {sentenceIndex}, Character {charIndex}")
                        
                        # Stop processing this sentence to prevent the DB crash
                        break 
                    else:
                        # 3. NEW: If it's unique, add it to the set so we can track it
                        seen_ids.add(textId)

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