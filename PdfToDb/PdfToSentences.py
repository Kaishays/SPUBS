import fitz  # PyMuPDF
import nltk
from nltk.tokenize import sent_tokenize

# This downloads the logic needed to detect sentence boundaries (run once)
#nltk.download('punkt_tab')

def pdf_to_sentences(pdf_path):
    # 1. Open and extract text
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    
    # 2. Clean the text
    # PDFs often have '\n' in the middle of sentences. 
    # This join/split replaces all newlines and tabs with single spaces.
    cleaned_text = " ".join(full_text.split())
    
    # 3. Convert string to array of sentences
    sentences = sent_tokenize(cleaned_text)
    
    return sentences

# --- Execution ---
# pdf_file_path = r".\data\Book7.pdf"
# sentence_array = pdf_to_sentences(pdf_file_path)

# To see it line-by-line:
# for i, s in enumerate(sentence_array):
#     print(f"Sentence {i}: {s}")