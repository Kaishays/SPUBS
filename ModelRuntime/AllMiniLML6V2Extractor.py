import numpy as np
from sentence_transformers import SentenceTransformer

class AllMiniLML6V2Extractor:
    def __init__(self, model_path):
        
        print(f"Loading SentenceTransformer model from: {model_path}...")
        self.model = SentenceTransformer(model_path)
        
        self.max_tokens = self.model.max_seq_length
        print(f"Model loaded successfully. Max input tokens: {self.max_tokens} (approx. {self.max_tokens * 4} characters)")

    def generate_embeddings(self, sentences, normalize=True):
       
        print(f"Generating embeddings (normalized={normalize})...")
        embeddings = self.model.encode(sentences, normalize_embeddings=normalize)

        return embeddings   