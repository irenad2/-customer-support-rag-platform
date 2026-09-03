"""
Step 3 - Governance & Security Layer
--------------------------------------
Applies access policies, masks PII before data enters the vector store,
and keeps an audit trail of every pipeline action (used later for the
architectural review / compliance evidence).
"""

import re
import json
import time
from pathlib import Path
from typing import Dict, Any

EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_RE = re.compile(r"\b\d{7,15}\b")


class GovernanceLayer:
    def __init__(self, audit_log_path: str = "logs/audit_log.jsonl"):
        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

    def mask_pii(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Redacts emails/phone numbers before data is embedded/indexed."""
        masked = dict(record)
        if masked.get("customer_email"):
            masked["customer_email"] = "[REDACTED_EMAIL]"
        for field in ("question", "resolution"):
            if masked.get(field):
                masked[field] = EMAIL_RE.sub("[EMAIL]", masked[field])
                masked[field] = PHONE_RE.sub("[PHONE]", masked[field])
        return masked

    def check_access(self, role: str, action: str) -> bool:
        """Very small policy table - extend as needed."""
        policies = {
            "agent": {"read", "query"},
            "admin": {"read", "query", "write", "delete"},
        }
        return action in policies.get(role, set())

    def log_audit(self, event: str, details: Dict[str, Any]):
        entry = {
            "timestamp": time.time(),
            "event": event,
            "details": details,
        }
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
