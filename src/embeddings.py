"""
Step 5 - Embedding & Vectorization Layer
-------------------------------------------
Converts ticket text into numeric vectors. Uses scikit-learn's TF-IDF
so the whole project runs fully offline with no external model
downloads. Swap `fit`/`embed` internals for a real embedding model
(e.g. sentence-transformers, OpenAI, or Cohere embeddings) in
production without touching any other layer - that is the point of
having this as its own module.
"""

from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class EmbeddingEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self._fitted = False

    def fit(self, texts: List[str]):
        self.vectorizer.fit(texts)
        self._fitted = True

    def embed(self, texts: List[str]) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("EmbeddingEngine must be fit() before embed().")
        matrix = self.vectorizer.transform(texts)
        return matrix.toarray()

    def embed_query(self, text: str) -> np.ndarray:
        return self.embed([text])[0]
