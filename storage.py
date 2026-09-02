"""
Step 4 - Data Storage (Lakehouse-style zones)
-----------------------------------------------
bronze/ = raw ingested data (as-is)
silver/ = validated + governed data (clean, PII-masked)

In production these would be Delta Lake / Iceberg tables on S3/ADLS,
queried through Databricks or Snowflake.
"""

import json
from pathlib import Path
from typing import List, Dict, Any


class LakehouseStorage:
    def __init__(self, base_path: str = "data"):
        self.bronze = Path(base_path) / "raw"
        self.silver = Path(base_path) / "processed"
        self.bronze.mkdir(parents=True, exist_ok=True)
        self.silver.mkdir(parents=True, exist_ok=True)

    def write_silver(self, records: List[Dict[str, Any]], filename: str = "tickets_clean.json"):
        path = self.silver / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        return str(path)

    def read_silver(self, filename: str = "tickets_clean.json") -> List[Dict[str, Any]]:
        path = self.silver / filename
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
