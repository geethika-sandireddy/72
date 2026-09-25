"""Run the required persistence/advection comparison on an authorized NPZ bundle.

Bundle format: one NPZ per case with arrays named observed_<horizon>, current_<horizon>,
and optional indra_<horizon>, dy_<horizon>, dx_<horizon>. This script never downloads
or labels data automatically.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
from app.benchmark import evaluate_replay

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("bundle", type=Path); parser.add_argument("--provenance", required=True); parser.add_argument("--output", type=Path, default=Path("artifacts/benchmark.json")); args=parser.parse_args()
    if not args.provenance.startswith("REPLAY:"): raise SystemExit("--provenance must be REPLAY:<case-id-or-split>")
    cases={}
    for path in sorted(args.bundle.glob("*.npz")):
        case={}; loaded=np.load(path)
        for horizon in (5,15,30,60,180):
            key=f"observed_{horizon}"
            if key not in loaded: continue
            sample={"observed":loaded[key],"current":loaded[f"current_{horizon}"]}
            for name in ("indra","dy","dx"):
                optional=f"{name}_{horizon}"
                if optional in loaded: sample[name]=loaded[optional]
            case[horizon]=sample
        if case: cases[path.stem]=case
    report=evaluate_replay(cases,args.provenance); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(json.dumps(report,indent=2)); print(json.dumps(report,indent=2)); return 0
if __name__ == "__main__": raise SystemExit(main())
