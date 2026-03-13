import sys
import os
from dotenv import find_dotenv, load_dotenv

# Make python aware of parent directories. 
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from PdfToSentences import pdf_to_sentences
from SentencesToDatabase import insert_sentences

load_dotenv(find_dotenv())

IP = os.getenv('DB_HOST')
PORT = int(os.getenv('DB_PORT'))
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
DATABASE = os.getenv('DB_NAME')

# New Environment Variables
PDF_PATH = os.getenv('PDF_PATH')
LOG_PATH = os.getenv('LOG_FILE_PATH')
SENTENCE_TABLE = os.getenv('SENTENCE_TABLE')
TARGET_PDF_ID = int(os.getenv('TARGET_PDF_ID'))

if __name__ == '__main__':
    sentences = pdf_to_sentences(PDF_PATH)
    insert_sentences(
        sentences=sentences, 
        host=IP, 
        port=PORT, 
        user=USER, 
        password=PASSWORD,
        database=DATABASE, 
        table=SENTENCE_TABLE, 
        pdfId=TARGET_PDF_ID,
        log_path=LOG_PATH 
    )