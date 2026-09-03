"""
Step 2 - Data Quality & Validation Layer
-----------------------------------------
Automated checks that block bad data before it reaches storage /
embeddings, similar in spirit to Great Expectations in production.
"""

from typing import Dict, Any, Tuple, List

REQUIRED_FIELDS = ["ticket_id", "category", "question", "resolution"]


class DataQualityValidator:
    def __init__(self):
        self.seen_ids = set()

    def validate(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Returns (is_valid, list_of_issues)."""
        issues = []

        # 1. Schema correctness / missing fields
        for field in REQUIRED_FIELDS:
            if field not in record or not str(record.get(field, "")).strip():
                issues.append(f"missing_or_empty_field:{field}")

        # 2. Duplicate detection
        ticket_id = record.get("ticket_id")
        if ticket_id in self.seen_ids:
            issues.append("duplicate_record")
        else:
            self.seen_ids.add(ticket_id)

        # 3. Invalid values
        if record.get("question") and len(record["question"]) < 5:
            issues.append("invalid_value:question_too_short")

        is_valid = len(issues) == 0
        return is_valid, issues

    def run_batch(self, records: List[Dict[str, Any]]):
        """Validate a batch, return (clean_records, rejected_records, report)."""
        clean, rejected = [], []
        for record in records:
            ok, issues = self.validate(record)
            if ok:
                clean.append(record)
            else:
                rejected.append({"record": record, "issues": issues})

        report = {
            "total": len(records),
            "passed": len(clean),
            "rejected": len(rejected),
        }
        return clean, rejected, report
