"""
Step 6 - Vector Storage
--------------------------
A minimal in-memory / on-disk vector store using cosine similarity.
Interface mirrors what you'd get from ChromaDB / Pinecone / Weaviate
(add(), search()), so this module can be swapped for one of those in
a production deployment without changing the RAG engine above it.
"""

import pickle
from pathlib import Path
from typing import List, Dict, Any
import numpy as np


class SimpleVectorStore:
    def __init__(self):
        self.ids: List[str] = []
        self.vectors: np.ndarray = None
        self.metadata: List[Dict[str, Any]] = []

    def add(self, ids: List[str], vectors: np.ndarray, metadata: List[Dict[str, Any]]):
        if self.vectors is None:
            self.vectors = vectors
        else:
            self.vectors = np.vstack([self.vectors, vectors])
        self.ids.extend(ids)
        self.metadata.extend(metadata)

    def search(self, query_vector: np.ndarray, top_k: int = 3):
        if self.vectors is None or len(self.ids) == 0:
            return []

        # cosine similarity
        norm_matrix = np.linalg.norm(self.vectors, axis=1)
        norm_query = np.linalg.norm(query_vector)
        denom = (norm_matrix * norm_query)
        denom[denom == 0] = 1e-10
        scores = (self.vectors @ query_vector) / denom

        top_idx = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_idx:
            results.append({
                "id": self.ids[idx],
                "score": float(scores[idx]),
                "metadata": self.metadata[idx],
            })
        return results

    def save(self, path: str = "data/processed/vector_store.pkl"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path: str = "data/processed/vector_store.pkl"):
        with open(path, "rb") as f:
            return pickle.load(f)
