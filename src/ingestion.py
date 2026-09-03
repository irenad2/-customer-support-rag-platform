"""
Step 1 - Data Ingestion
-----------------------
In production this layer would be Kafka/Flink/Airflow pulling from live
APIs, CRMs, chat systems, etc. Here we simulate a real-time source by
streaming records from a local JSON file, one ticket at a time, so the
rest of the pipeline (quality -> governance -> storage -> embeddings ->
vector DB -> RAG) can be demonstrated end-to-end without external infra.
"""

import json
import time
from pathlib import Path
from typing import Iterator, Dict, Any


class TicketStream:
    """Simulates a real-time stream of customer support tickets."""

    def __init__(self, source_path: str):
        self.source_path = Path(source_path)

    def stream(self, delay: float = 0.0) -> Iterator[Dict[str, Any]]:
        """Yield one ticket at a time, like a live pipeline would."""
        with open(self.source_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        for record in records:
            if delay:
                time.sleep(delay)
            yield record

    def load_all(self) -> list:
        """Bulk load (used for batch/replay scenarios)."""
        with open(self.source_path, "r", encoding="utf-8") as f:
            return json.load(f)
