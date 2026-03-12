import numpy as np
from sentence_transformers import SentenceTransformer

class AllMiniLML6V2Extractor:
    def __init__(self, model_path):
        """
        Initializes the model from the given local path or HuggingFace hub.
        Loading happens only once when the class is instantiated.
        """
        print(f"Loading SentenceTransformer model from: {model_path}...")
        self.model = SentenceTransformer(model_path)
        
        self.max_tokens = self.model.max_seq_length
        print(f"Model loaded successfully. Max input tokens: {self.max_tokens} (approx. {self.max_tokens * 4} characters)")

    def generate_embeddings(self, sentences, normalize=True):
        """
        Generates embeddings for a list of sentences or a single sentence.
        Set normalize=True (default) to return L2-normalized vectors.
        """
        print(f"Generating embeddings (normalized={normalize})...")
        # The built-in normalize_embeddings=True is highly optimized
        embeddings = self.model.encode(sentences, normalize_embeddings=normalize)

        if normalize:
            embeddings = self.normalize_manual(embeddings)

        return embeddings   

    def normalize_manual(self, embeddings):
        """
        Manually applies L2 normalization to a numpy array of embeddings.
        Useful if you have raw embeddings that were generated with normalize=False.
        """
        print("Manually normalizing embeddings...")
        # Ensure it's a numpy array
        embeddings = np.array(embeddings)
        
        # Calculate the L2 norm along the feature axis (divide by magnituide)
        # keepdims=True ensures the shape aligns for broadcasting during division
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Avoid division by zero by replacing 0 norms with a tiny number
        norms[norms == 0] = 1e-10 
        
        normalized_embeddings = embeddings / norms
        return normalized_embeddings


# ==========================================
# Example Usage / Quick Test
# ==========================================
if __name__ == "__main__":
    test_path = 'all-MiniLM-L6-v2' # Using HF hub name for general testing
    
    # 1. Instantiate the class
    extractor = AllMiniLML6V2Extractor(test_path)
    
    # 2. Define test data
    test_sentences = ["Harry raised his wand.", "The Dementor swooped down."]
    
    # 3. Generate embeddings using the built-in normalization
    test_embeddings_auto = extractor.generate_embeddings(test_sentences, normalize=True)
    
    # 4. Generate raw embeddings and manually normalize them
    test_embeddings_raw = extractor.generate_embeddings(test_sentences, normalize=False)
    test_embeddings_manual = extractor.normalize_manual(test_embeddings_raw)
    
    print(f"Generated {len(test_embeddings_auto)} embeddings.")
    print(f"Dimensions of first embedding: {len(test_embeddings_auto[0])}")
    
    # Quick check to prove vectors are normalized (magnitude should be ~1.0)
    magnitude_auto = np.linalg.norm(test_embeddings_auto[0])
    magnitude_manual = np.linalg.norm(test_embeddings_manual[0])
    print(f"Magnitude of auto-normalized vector: {magnitude_auto:.4f}")
    print(f"Magnitude of manually normalized vector: {magnitude_manual:.4f}")