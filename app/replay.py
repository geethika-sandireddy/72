"""Replay-case registry with strict provenance and source inventory."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json

@dataclass
class ReplayCase:
    case_id: str; path: str; description: str; sources: list[str]; created_utc: str; provenance: str
    def as_dict(self): return asdict(self)

class ReplayCaseManager:
    def __init__(self, root: str="data/replay"):
        self.root=Path(root)
    def list_cases(self):
        cases=[]
        if not self.root.exists(): return cases
        for metadata in sorted(self.root.glob("*/metadata.json")):
            data=json.loads(metadata.read_text()); data.setdefault("path",str(metadata.parent)); data.setdefault("provenance",f"REPLAY:{data['case_id']}"); cases.append(ReplayCase(**data))
        return cases
    def load(self, case_id: str):
        path=self.root/case_id/"metadata.json"
        if not path.exists(): raise FileNotFoundError(f"replay case not found: {case_id}")
        data=json.loads(path.read_text()); data["path"]=str(path.parent); data.setdefault("provenance",f"REPLAY:{case_id}"); return ReplayCase(**data)
    def template(self, case_id: str, description: str="Authorized historical case"):
        path=self.root/case_id; path.mkdir(parents=True,exist_ok=True)
        data={"case_id":case_id,"description":description,"sources":[],"created_utc":datetime.now(timezone.utc).isoformat(),"provenance":f"REPLAY:{case_id}"}
        (path/"metadata.json").write_text(json.dumps(data,indent=2)); return self.load(case_id)
