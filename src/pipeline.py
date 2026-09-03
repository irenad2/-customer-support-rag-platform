"""
Orchestrates the full architecture, step by step, exactly matching the
"How All Components Work Together" flow from the course:

  1. Data Ingestion
  2. Data Quality Validation
  3. Governance Enforcement
  4. Data Storage
  5. Embedding Generation
  6. Vector Storage
  7. RAG Retrieval
  8. AI Response Generation
"""

from .ingestion import TicketStream
from .data_quality import DataQualityValidator
from .governance import GovernanceLayer
from .storage import LakehouseStorage
from .embeddings import EmbeddingEngine
from .vector_store import SimpleVectorStore
from .rag_engine import RAGEngine


class SupportIntelligencePlatform:
    def __init__(self, source_path: str = "data/raw/tickets.json"):
        self.source_path = source_path
        self.quality = DataQualityValidator()
        self.governance = GovernanceLayer()
        self.storage = LakehouseStorage()
        self.embedder = EmbeddingEngine()
        self.vector_store = SimpleVectorStore()
        self.rag = None

    def build_index(self, verbose: bool = True):
        # Step 1 - Ingestion
        stream = TicketStream(self.source_path)
        raw_records = stream.load_all()
        if verbose:
            print(f"[1/8] Ingested {len(raw_records)} raw tickets.")

        # Step 2 - Data Quality Validation
        clean, rejected, report = self.quality.run_batch(raw_records)
        self.governance.log_audit("data_quality_check", report)
        if verbose:
            print(f"[2/8] Quality check -> passed: {report['passed']}, rejected: {report['rejected']}")

        # Step 3 - Governance Enforcement (PII masking + audit)
        governed = [self.governance.mask_pii(r) for r in clean]
        self.governance.log_audit("pii_masking_applied", {"count": len(governed)})
        if verbose:
            print(f"[3/8] Governance applied to {len(governed)} records (PII masked).")

        # Step 4 - Data Storage (silver zone)
        path = self.storage.write_silver(governed)
        if verbose:
            print(f"[4/8] Clean data stored at: {path}")

        # Step 5 - Embedding Generation
        texts = [f"{r['question']} {r['resolution']}" for r in governed]
        self.embedder.fit(texts)
        vectors = self.embedder.embed(texts)
        if verbose:
            print(f"[5/8] Generated embeddings, shape={vectors.shape}")

        # Step 6 - Vector Storage
        ids = [r["ticket_id"] for r in governed]
        self.vector_store.add(ids, vectors, governed)
        self.vector_store.save()
        if verbose:
            print(f"[6/8] Stored {len(ids)} vectors in the vector database.")

        self.rag = RAGEngine(self.embedder, self.vector_store)
        return report

    def ask(self, question: str, top_k: int = 3, role: str = "agent"):
        if self.rag is None:
            raise RuntimeError("Call build_index() before ask().")

        if not self.governance.check_access(role, "query"):
            return {"error": f"role '{role}' is not authorized to query the platform."}

        # Step 7 - RAG Retrieval
        contexts = self.rag.retrieve(question, top_k=top_k * 2, rerank_top=top_k)

        # Step 8 - AI Response Generation
        answer = self.rag.generate(question, contexts)

        self.governance.log_audit("query", {
            "question": question,
            "role": role,
            "sources": [c["metadata"]["ticket_id"] for c in contexts],
        })

        return {
            "question": question,
            "answer": answer,
            "sources": [
                {"ticket_id": c["metadata"]["ticket_id"], "score": round(c["rerank_score"], 3)}
                for c in contexts
            ],
        }
