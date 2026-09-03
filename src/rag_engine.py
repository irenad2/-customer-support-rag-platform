"""
Step 7 & 8 - Advanced RAG System + AI Response Generation
------------------------------------------------------------
Retrieval  : semantic search against the vector store.
Re-ranking : simple keyword-overlap boost on top of cosine similarity
             (stand-in for a cross-encoder reranker in production).
Generation : if an ANTHROPIC_API_KEY environment variable is present,
             calls the real Claude API for a grounded answer. Otherwise
             falls back to a deterministic, extractive template so the
             whole pipeline works with zero external dependencies.
"""

import os
from typing import List, Dict, Any

from .embeddings import EmbeddingEngine
from .vector_store import SimpleVectorStore


def _keyword_overlap(query: str, text: str) -> float:
    q_tokens = set(query.lower().split())
    t_tokens = set(text.lower().split())
    if not q_tokens:
        return 0.0
    return len(q_tokens & t_tokens) / len(q_tokens)


class RAGEngine:
    def __init__(self, embedding_engine: EmbeddingEngine, vector_store: SimpleVectorStore):
        self.embedding_engine = embedding_engine
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5, rerank_top: int = 3) -> List[Dict[str, Any]]:
        query_vector = self.embedding_engine.embed_query(query)
        candidates = self.vector_store.search(query_vector, top_k=top_k)

        # Re-ranking step: blend cosine score with keyword overlap
        for c in candidates:
            text = c["metadata"].get("question", "") + " " + c["metadata"].get("resolution", "")
            overlap = _keyword_overlap(query, text)
            c["rerank_score"] = 0.7 * c["score"] + 0.3 * overlap

        candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        return candidates[:rerank_top]

    def generate(self, query: str, contexts: List[Dict[str, Any]]) -> str:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            return self._generate_with_claude(query, contexts, api_key)
        return self._generate_extractive(query, contexts)

    def _generate_extractive(self, query: str, contexts: List[Dict[str, Any]]) -> str:
        if not contexts:
            return "No relevant past tickets were found for this question."

        best = contexts[0]["metadata"]
        sources = ", ".join(c["metadata"]["ticket_id"] for c in contexts)
        answer = (
            f"Based on similar past tickets ({sources}), the likely resolution is:\n"
            f"{best['resolution']}"
        )
        return answer

    def _generate_with_claude(self, query: str, contexts: List[Dict[str, Any]], api_key: str) -> str:
        try:
            import anthropic
        except ImportError:
            return self._generate_extractive(query, contexts)

        context_text = "\n\n".join(
            f"[{c['metadata']['ticket_id']}] Q: {c['metadata']['question']}\n"
            f"Resolution: {c['metadata']['resolution']}"
            for c in contexts
        )
        prompt = (
            "You are a customer support assistant. Using ONLY the context below, "
            "answer the new customer question and cite the ticket IDs you used.\n\n"
            f"Context:\n{context_text}\n\nNew question: {query}\n\nAnswer:"
        )
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
