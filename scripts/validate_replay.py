"""Validate authorized replay-case manifests before training or serving.

This command validates metadata and directory structure only. It never promotes
synthetic data to replay data and never downloads data implicitly.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from datetime import datetime

REQUIRED = ("case_id", "provenance", "sources", "domain", "master_cadence_minutes",
            "observation_start_utc", "observation_end_utc", "license_or_access_note", "raw_data_owner")


def validate_case(case: Path) -> list[str]:
    errors: list[str] = []
    metadata = case / "metadata.json"
    if not metadata.exists():
        return [f"{case}: missing metadata.json"]
    try:
        data = json.loads(metadata.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{metadata}: invalid JSON: {exc}"]
    for key in REQUIRED:
        if key not in data or data[key] in (None, "", []): errors.append(f"{metadata}: missing {key}")
    expected = f"REPLAY:{data.get('case_id', '')}"
    if data.get("provenance") != expected: errors.append(f"{metadata}: provenance must be {expected!r}")
    domain = data.get("domain", {})
    for key in ("lat_min", "lat_max", "lon_min", "lon_max", "crs"):
        if key not in domain: errors.append(f"{metadata}: domain missing {key}")
    if domain.get("lat_min", 0) >= domain.get("lat_max", 0): errors.append(f"{metadata}: invalid latitude bounds")
    if domain.get("lon_min", 0) >= domain.get("lon_max", 0): errors.append(f"{metadata}: invalid longitude bounds")
    try:
        datetime.fromisoformat(str(data.get("observation_start_utc", "")).replace("Z", "+00:00"))
        datetime.fromisoformat(str(data.get("observation_end_utc", "")).replace("Z", "+00:00"))
    except ValueError: errors.append(f"{metadata}: timestamps must be ISO-8601")
    if not isinstance(data.get("master_cadence_minutes"), int) or data["master_cadence_minutes"] <= 0:
        errors.append(f"{metadata}: master_cadence_minutes must be a positive integer")
    for directory in ("radar", "satellite", "lightning", "nwp", "labels"):
        if not (case / directory).exists(): errors.append(f"{case}: expected directory missing: {directory}/")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default="data/replay")
    args = parser.parse_args()
    root = Path(args.root)
    cases = [p for p in root.iterdir() if p.is_dir()] if root.exists() else []
    cases = [p for p in cases if (p / "metadata.json").exists()]
    if not cases:
        print(f"No replay cases found under {root}. Synthetic demo remains the only runnable mode.")
        return 0
    all_errors = [error for case in cases for error in validate_case(case)]
    if all_errors:
        print("Replay validation failed:")
        print("\n".join(f"- {error}" for error in all_errors))
        return 1
    print(f"Validated {len(cases)} replay case manifest(s); no raw data were relabeled.")
    return 0

if __name__ == "__main__": raise SystemExit(main())
