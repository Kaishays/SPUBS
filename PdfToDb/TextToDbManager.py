import sys
import os

# Make python aware of parent directories. 
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from PdfToSentences import pdf_to_sentences
from SentencesToDatabase import insert_sentences
import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

IP = os.getenv('DB_HOST')
PORT = int(os.getenv('DB_PORT'))
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
DATABASE = os.getenv('DB_NAME')

if __name__ == '__main__':
    pdf_path = r".\data\Book6.pdf"
    sentences = pdf_to_sentences(pdf_path)
    insert_sentences(sentences, host=IP, port=PORT, user=USER, password=PASSWORD,
                     database=DATABASE, table='pdf_sentences', bookId=6)
    