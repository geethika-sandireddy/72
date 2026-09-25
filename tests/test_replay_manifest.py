"""Tests for data truthfulness and replay manifest validation."""
import json
from pathlib import Path
from scripts.validate_replay import validate_case

def test_template_is_not_accepted_as_a_case(tmp_path: Path):
    case = tmp_path / "case"
    case.mkdir()
    (case / "metadata.json").write_text(json.dumps({"case_id": "case", "provenance": "SYNTHETIC"}))
    assert validate_case(case)

def test_valid_manifest_structure(tmp_path: Path):
    case = tmp_path / "case-1"
    for directory in ("radar", "satellite", "lightning", "nwp", "labels"):
        (case / directory).mkdir(parents=True)
    metadata = {
        "case_id": "case-1", "provenance": "REPLAY:case-1", "sources": ["authorized"],
        "domain": {"lat_min": 15, "lat_max": 20, "lon_min": 75, "lon_max": 80, "crs": "EPSG:4326"},
        "master_cadence_minutes": 15, "observation_start_utc": "2025-01-01T00:00:00Z",
        "observation_end_utc": "2025-01-01T01:00:00Z", "license_or_access_note": "authorized",
        "raw_data_owner": "hackathon team"
    }
    (case / "metadata.json").write_text(json.dumps(metadata))
    assert validate_case(case) == []
