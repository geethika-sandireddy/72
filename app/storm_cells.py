"""Standalone TITAN-style connected-component storm cell detector/tracker."""
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
import numpy as np
from scipy import ndimage

@dataclass
class StormCell:
    cell_id: int
    centroid_y: float
    centroid_x: float
    area: int
    max_reflectivity: float
    motion_y: float = 0.0
    motion_x: float = 0.0
    area_growth: float = 0.0
    max_reflectivity_trend: float = 0.0
    provenance: str = "SYNTHETIC"
    def as_dict(self): return asdict(self)

class StormCellTracker:
    def __init__(self, threshold_dbz: float = 35.0, min_area: int = 3):
        self.threshold_dbz, self.min_area = threshold_dbz, min_area
        self.previous: Dict[int, StormCell] = {}
        self.next_id = 1
    def detect(self, composite_reflectivity: np.ndarray, provenance: str) -> List[StormCell]:
        mask = np.asarray(composite_reflectivity) >= self.threshold_dbz
        labels, count = ndimage.label(mask, structure=np.ones((3, 3)))
        cells = []
        for label in range(1, count + 1):
            ys, xs = np.where(labels == label)
            if len(xs) < self.min_area: continue
            values = composite_reflectivity[ys, xs]
            cells.append(StormCell(self.next_id, float(ys.mean()), float(xs.mean()),
                                   len(xs), float(values.max()), provenance=provenance))
            self.next_id += 1
        return cells
    def update(self, field: np.ndarray, provenance: str = "SYNTHETIC") -> List[StormCell]:
        current = self.detect(field, provenance)
        for cell in current:
            if self.previous:
                old = min(self.previous.values(), key=lambda c: (c.centroid_y-cell.centroid_y)**2 + (c.centroid_x-cell.centroid_x)**2)
                cell.motion_y, cell.motion_x = cell.centroid_y-old.centroid_y, cell.centroid_x-old.centroid_x
                cell.area_growth = (cell.area-old.area) / max(old.area, 1)
                cell.max_reflectivity_trend = cell.max_reflectivity-old.max_reflectivity
            self.previous[cell.cell_id] = cell
        return current
    @staticmethod
    def features(cell: StormCell) -> Dict[str, float]:
        return {"cell_motion_y": cell.motion_y, "cell_motion_x": cell.motion_x,
                "cell_area": float(cell.area), "cell_area_growth": cell.area_growth,
                "max_reflectivity": cell.max_reflectivity,
                "max_reflectivity_trend": cell.max_reflectivity_trend}
