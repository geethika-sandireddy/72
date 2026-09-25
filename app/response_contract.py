"""Stable replay/live/synthetic response contracts for the operator console."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict

def observation_time(request):
    stamps=[]
    for group in (request.radar, request.satellite, request.nwp):
        stamps.extend(o.meta.timestamp_utc for o in group.values())
    stamps.extend(e.timestamp_utc for e in request.lightning)
    return max(stamps).isoformat() if stamps else None

def forecast_meta(request, start: float, model_report: Dict[str, Any]):
    now=datetime.now(timezone.utc)
    return {"generated_at_utc": now.isoformat(), "observation_time_utc": observation_time(request),
            "provenance": request.provenance, "case_id": request.case_id,
            "latency_ms": round((now.timestamp()-start)*1000, 2),
            "model": model_report,
            "uncertainty_status": "heuristic_demo_interval; calibration not claimed" if request.provenance == "SYNTHETIC" else "not_calibrated",
            "official_warning_issued": False}
