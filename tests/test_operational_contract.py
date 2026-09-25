"""Focused smoke tests for the truthful operator API contract."""
from datetime import datetime, timezone
from app.contracts import NowcastRequest
from app.operational import source_health, evidence_summary

def test_synthetic_health_is_explicit():
    request=NowcastRequest(provenance="SYNTHETIC")
    assert all(row["status"] == "SYNTHETIC" for row in source_health(request))

def test_missing_real_sources_are_not_live():
    request=NowcastRequest(provenance="LIVE", radar_field=[[1,2],[3,4]])
    rows=source_health(request)
    assert {row["source"]: row["status"] for row in rows}["SATELLITE"] == "MISSING"

def test_availability_is_not_agreement():
    request=NowcastRequest(provenance="SYNTHETIC")
    result=evidence_summary(request, [[20, 50], [30, 60]], agreement=None)
    assert result["availability_fraction"] == 0
    assert result["agreement"] is None
