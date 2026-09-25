"""Input validation helpers for real-data requests; no hidden meteorology defaults."""
from fastapi import HTTPException

def require_observation_time(meta, source: str):
    if meta is None or meta.timestamp_utc is None: raise HTTPException(422,f"{source} requires observation timestamp")

def require_complete_modality(req, allow_degraded=True):
    present={"radar":bool(req.radar),"satellite":bool(req.satellite),"lightning":bool(req.lightning),"nwp":bool(req.nwp)}
    if req.provenance in {"LIVE"} and not any(present.values()): raise HTTPException(400,"LIVE request has no observations")
    return present
