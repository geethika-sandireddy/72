"""Operational evidence helpers used by the API and dashboard.

This module deliberately separates source availability, freshness and cross-source
evidence. A source being present is never treated as proof that sources agree.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Mapping
import numpy as np

SOURCE_GROUPS = {
    "RADAR": "radar",
    "SATELLITE": "satellite",
    "LIGHTNING": "lightning",
    "NWP": "nwp",
}

def source_timestamp(group: str, payload: Mapping[str, Any]):
    if group == "lightning":
        stamps = [e.timestamp_utc for e in payload] if payload else []
    else:
        stamps = [o.meta.timestamp_utc for o in payload.values()] if payload else []
    return max(stamps) if stamps else None

def source_health(request, now: datetime | None = None):
    now = now or datetime.now(timezone.utc)
    rows = []
    for label, attr in SOURCE_GROUPS.items():
        payload = getattr(request, attr)
        stamp = source_timestamp(attr, payload)
        if request.provenance == "SYNTHETIC":
            status = "SYNTHETIC"
            age = None
        elif not payload:
            status = "MISSING"
            age = None
        else:
            age = max(0.0, (now - stamp).total_seconds() / 60.0) if stamp else None
            status = "DELAYED" if age is not None and age > 15 else ("LIVE" if request.provenance == "LIVE" else "REPLAY")
        rows.append({"source": label, "status": status, "provenance": request.provenance,
                     "latency_minutes": None if age is None else round(age, 2),
                     "observation_timestamp_utc": stamp.isoformat() if stamp else None})
    return rows

def evidence_summary(request, radar_field, agreement: float | None = None):
    field = np.asarray(radar_field, dtype=float)
    radar_signal = float(np.clip((np.nanpercentile(field, 90) - 30) / 35, 0, 1)) if field.size else 0.0
    lightning_count = len(request.lightning)
    lightning_signal = float(np.clip(lightning_count / 12, 0, 1))
    present = {label: bool(getattr(request, attr)) for label, attr in SOURCE_GROUPS.items()}
    evidence = {"RADAR": round(radar_signal, 3), "SATELLITE": None,
                "LIGHTNING": round(lightning_signal, 3) if present["LIGHTNING"] else None,
                "NWP": None}
    available = sum(present.values()) / len(present)
    return {"availability_fraction": round(available, 3), "agreement": agreement,
            "source_present": present, "evidence": evidence,
            "note": "Agreement is based on evidence scale only when modality evidence exists; availability is not agreement."}
