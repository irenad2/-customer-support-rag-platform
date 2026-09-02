"""
Real-Time Customer Support Intelligence Platform
--------------------------------------------------
Final capstone project - Modern Data Engineering for AI Systems (SDAIA).

Run:
    python main.py                     -> runs the demo questions
    python main.py "your question"     -> ask a single custom question
"""

import sys
import json
from src.pipeline import SupportIntelligencePlatform

DEMO_QUESTIONS = [
    "A customer says they were billed twice, what should I do?",
    "Customer can't log in even after resetting the password.",
    "How long is the return window for an order?",
]


def main():
    print("=" * 60)
    print(" Building the Integrated AI Data Platform ")
    print("=" * 60)

    platform = SupportIntelligencePlatform(source_path="data/raw/tickets.json")
    platform.build_index()

    print("\n" + "=" * 60)
    print(" Querying the RAG system ")
    print("=" * 60)

    questions = [sys.argv[1]] if len(sys.argv) > 1 else DEMO_QUESTIONS

    for q in questions:
        result = platform.ask(q)
        print(f"\nQ: {result['question']}")
        print(f"A: {result['answer']}")
        print(f"Sources: {result['sources']}")

    print("\nAudit log written to logs/audit_log.jsonl")


if __name__ == "__main__":
    main()
