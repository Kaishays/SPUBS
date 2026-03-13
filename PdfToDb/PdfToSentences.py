import fitz  # PyMuPDF
from nltk.tokenize import sent_tokenize

def pdf_to_sentences(pdf_path):

    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    
    #Split returns a list of words, and join concatenates them with a single space, effectively removing extra spaces.
    cleaned_text = " ".join(full_text.split())
    
    # Use NLTK's sent_tokenize to split the cleaned text into sentences.
    sentences = sent_tokenize(cleaned_text)
    
    return sentences