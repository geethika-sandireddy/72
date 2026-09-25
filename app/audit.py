"""Tamper-evident forecast/audit event records for operational review."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib, json

@dataclass
class AuditEvent:
    event_id: str; event_type: str; provenance: str; payload_hash: str; created_utc: str
    def as_dict(self): return asdict(self)

def make_audit_event(event_id: str, event_type: str, payload, provenance: str) -> AuditEvent:
    canonical=json.dumps(payload,sort_keys=True,default=str).encode("utf-8")
    digest=hashlib.sha256(canonical).hexdigest()
    return AuditEvent(event_id,event_type,provenance,digest,datetime.now(timezone.utc).isoformat())
