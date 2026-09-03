# Real-Time Customer Support Intelligence Platform

**Final Capstone Project — Modern Data Engineering for AI Systems**
Course by [Saudi Data & AI Authority (SDAIA)](https://sdaia.gov.sa)

## 1. Overview

This project is the final capstone for the *"Modern Data Engineering for AI
Systems"* course (Day 5 — Architecture Integration and Final Project). It
integrates every architectural component covered throughout the course into
**one working, end-to-end platform**:

- Modern Data Architecture (Lakehouse-style storage zones)
- Real-Time Data Pipelines (simulated ingestion stream)
- Data Quality Framework (schema, missing-field, and duplicate checks)
- Data Governance (PII masking, role-based access, audit logging)
- Embedding & Vectorization Layer
- Vector Database (lightweight, swappable with Pinecone/ChromaDB/Weaviate)
- Advanced RAG System (retrieval + re-ranking + answer generation)
- AI Application layer (a support-agent Q&A assistant)

The chosen use case is **Idea 1** from the course brief: a platform that
ingests customer support tickets and knowledge base articles, validates and
governs them, and lets support agents ask natural-language questions to get
grounded, cited answers from past resolved tickets.

> The project runs **fully offline** with zero external services or API
> keys required — every heavy production tool (Kafka, Spark, ChromaDB,
> a hosted embedding model) is represented by a lightweight local
> equivalent so the whole pipeline can be demoed end-to-end in seconds.
> Each module is isolated so any of these can be swapped for the real
> production tool without touching the rest of the architecture.

## 2. Architecture

```
+--------------------------+
|      Data Sources        |   Support tickets, chat transcripts, KB articles
|  (APIs / CRM / Files)    |
+--------------------------+
             |
             v
+--------------------------+
| 1. Real-Time Ingestion   |   src/ingestion.py
+--------------------------+
             |
             v
+--------------------------+
| 2. Data Quality &        |   src/data_quality.py
|    Validation Layer      |   (schema / missing fields / duplicates)
+--------------------------+
             |
             v
+--------------------------+
| 3. Governance & Security |   src/governance.py
|    Layer                 |   (PII masking, access control, audit log)
+--------------------------+
             |
             v
+--------------------------+
| 4. Lakehouse Storage     |   src/storage.py
|    (bronze / silver)     |
+--------------------------+
             |
             v
+--------------------------+
| 5. Embedding &           |   src/embeddings.py
|    Vectorization Layer   |
+--------------------------+
             |
             v
+--------------------------+
| 6. Vector Database       |   src/vector_store.py
+--------------------------+
             |
             v
+--------------------------+
| 7. Advanced RAG System   |   src/rag_engine.py
|    (retrieve + re-rank)  |
+--------------------------+
             |
             v
+--------------------------+
| 8. AI Response Generation|   src/rag_engine.py (generate)
+--------------------------+
             |
             v
+--------------------------+
|  AI Application (CLI)    |   main.py
+--------------------------+
```

This mirrors the "How All Components Work Together" flow from the course
(Steps 1–8) and the *High-Level Unified Architecture* diagram from the
final lecture.

## 3. Tech Stack

| Layer              | Used in this project        | Production-grade equivalent      |
|---------------------|------------------------------|-----------------------------------|
| Data Pipelines       | Python generator stream      | Kafka, Spark, Flink, Airflow      |
| Storage              | Local JSON (bronze/silver)   | Databricks Lakehouse, Snowflake   |
| Data Quality         | Custom validator             | Great Expectations                |
| Governance           | Custom PII masking + audit   | Collibra, Microsoft Purview       |
| Embeddings           | scikit-learn TF-IDF          | Sentence Transformers, OpenAI     |
| Vector Database      | In-memory cosine-sim store   | Pinecone, ChromaDB, Weaviate      |
| RAG Orchestration    | Custom retrieval + re-rank   | LangChain, LlamaIndex             |
| LLM Generation       | Extractive fallback / Claude | GPT, Claude, Qwen                 |

## 4. Project Structure

```
customer-support-rag-platform/
├── data/
│   ├── raw/tickets.json          # simulated real-time source (bronze)
│   └── processed/                # cleaned & governed data (silver)
├── logs/
│   └── audit_log.jsonl           # governance audit trail (generated at runtime)
├── src/
│   ├── ingestion.py              # Step 1
│   ├── data_quality.py           # Step 2
│   ├── governance.py             # Step 3
│   ├── storage.py                # Step 4
│   ├── embeddings.py             # Step 5
│   ├── vector_store.py           # Step 6
│   ├── rag_engine.py             # Step 7 & 8
│   └── pipeline.py               # Orchestrates all 8 steps
├── main.py                       # CLI entry point / demo
├── requirements.txt
└── README.md
```

## 5. Setup & Run

```bash
# 1. Clone the repo
git clone <YOUR_GITHUB_REPO_URL>
cd customer-support-rag-platform

# 2. Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the demo pipeline
python main.py

# 5. (Optional) Ask your own question
python main.py "How do I update my payment method?"
```

### Enabling real LLM generation (optional)

By default, answers are generated with a deterministic extractive
template so the project needs no API key. To use a real LLM instead:

```bash
export ANTHROPIC_API_KEY=your_key_here
python main.py "A customer says they were billed twice, what should I do?"
```

## 6. What Happens When You Run It

1. **Ingestion** — streams sample tickets from `data/raw/tickets.json`.
2. **Data Quality** — rejects any record with missing fields, duplicates,
   or invalid values, and reports pass/fail counts.
3. **Governance** — masks customer emails/phone numbers and writes every
   action to `logs/audit_log.jsonl`.
4. **Storage** — writes the clean, governed data to the silver zone
   (`data/processed/tickets_clean.json`).
5. **Embeddings** — vectorizes ticket text (TF-IDF).
6. **Vector Storage** — indexes the vectors for semantic search.
7. **RAG Retrieval** — for each question, retrieves and re-ranks the most
   relevant past tickets.
8. **AI Response Generation** — produces a grounded answer citing the
   source ticket IDs.

## 7. Enterprise Benefits Demonstrated

- **Unified AI Ecosystem** — ingestion, governance, storage, and AI all run
  through one pipeline.
- **Better AI Accuracy / Reduced Hallucinations** — answers are grounded in
  retrieved, governed source tickets and always cite their sources.
- **Governance & Compliance** — PII is masked before indexing, and every
  query and pipeline action is logged for audit.
- **Scalability path** — every module has a clearly marked production
  upgrade path (see Tech Stack table).

## 8. Known Limitations (by design, for a same-day demo)

- Embeddings use TF-IDF instead of a trained neural embedding model, so
  semantic matching is weaker than a production RAG system — swap in
  `sentence-transformers` or an API-based embedding model for better
  retrieval quality.
- The vector store is in-memory/pickle-based rather than a managed vector
  database — the interface (`add()`, `search()`) is intentionally
  compatible with swapping in ChromaDB/Pinecone.
- The sample dataset (8 tickets) is for demonstration only.

## 9. Course Reference

This project was built as the final capstone for the **Modern Data
Engineering for AI Systems** course by the
[Saudi Data & AI Authority (SDAIA)](https://sdaia.gov.sa) — Day 5:
*Architecture Integration and Final Project*.
