"""Persistent per-case temporal state for tracker and LAD cells."""
from dataclasses import dataclass, field
from typing import Dict, List
from app.lad_model import LADCell
from app.storm_cells import StormCellTracker

@dataclass
class CaseState:
    tracker: StormCellTracker = field(default_factory=StormCellTracker)
    lad_by_cell: Dict[int, LADCell] = field(default_factory=dict)
    timestamps: List[str] = field(default_factory=list)

class CaseStateStore:
    def __init__(self): self._cases: Dict[str, CaseState] = {}
    def get(self, case_id: str) -> CaseState:
        return self._cases.setdefault(case_id, CaseState())
    def clear(self, case_id: str): self._cases.pop(case_id, None)
    def summary(self, case_id: str):
        state=self.get(case_id)
        return {"case_id":case_id,"frames":len(state.timestamps),"tracked_cells":len(state.tracker.previous)}
