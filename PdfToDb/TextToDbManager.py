from PdfToSentences import pdf_to_sentences
from SentencesToDatabase import insert_sentences
IP = 'localhost'
PORT = 3306
USER = 'root'
PASSWORD = '132312ADADADAqeqeqeqe#!#!#!#!!#!KJLKJ'
DATABASE = 'harry_potter_semantics'

if __name__ == '__main__':
    pdf_path = r".\data\Book7.pdf"
    sentences = pdf_to_sentences(pdf_path)
    insert_sentences(sentences, host=IP, port=PORT, user=USER, password=PASSWORD,
                     database=DATABASE, table='harrypottersentences', bookId=7)
    