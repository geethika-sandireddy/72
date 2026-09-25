"""Convert a small SEVIR-style event bundle into INDRA replay metadata.

This is a provenance-preserving bridge, not an India validation claim. It records
SEVIR as an external real benchmark and requires the operator to provide actual
arrays/labels after selecting an event. No synthetic labels are generated here.
"""
from __future__ import annotations
import argparse,json
from datetime import datetime,timezone
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument("case_id"); p.add_argument("--root",type=Path,default=Path("data/external/sevir")); p.add_argument("--output",type=Path,default=Path("data/replay")); args=p.parse_args()
    case=args.output/args.case_id; case.mkdir(parents=True,exist_ok=True)
    for name in ("radar","satellite","lightning","nwp","labels"): (case/name).mkdir(exist_ok=True)
    metadata={"case_id":args.case_id,"provenance":f"REPLAY:{args.case_id}","description":"SEVIR real-event benchmark bridge; US domain, not India operational validation.","sources":["SEVIR_NEXRAD_VIL","SEVIR_GOES_IR","SEVIR_GOES_GLM"],"domain":{"lat_min":0.0,"lat_max":1.0,"lon_min":0.0,"lon_max":1.0,"crs":"EPSG:4326"},"master_cadence_minutes":5,"observation_start_utc":datetime.now(timezone.utc).isoformat(),"observation_end_utc":datetime.now(timezone.utc).isoformat(),"license_or_access_note":"Public SEVIR benchmark; verify upstream terms before redistribution.","raw_data_owner":"MIT AI Accelerator / SEVIR public benchmark","source_root":str(args.root),"label_status":"operator must map selected real event arrays; no labels fabricated"}
    (case/"metadata.json").write_text(json.dumps(metadata,indent=2)); print(case); return 0
if __name__ == "__main__": raise SystemExit(main())
