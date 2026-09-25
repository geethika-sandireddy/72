"""Transparent impact and arrival-time decision layer for district operations."""
from dataclasses import dataclass, asdict
from math import hypot
from typing import Iterable, Optional

@dataclass
class ImpactAssessment:
    district: str; hazard: str; maximum_probability: float; arrival_minutes: Optional[float]
    level: str; action: str; provenance: str
    def as_dict(self): return asdict(self)

def assess_district(district: str, probability: float, cell_xy: tuple[float,float]=(0.,0.),
                    district_xy: tuple[float,float]=(0.,0.), speed_pixels_per_minute: float=0.,
                    hazard: str="thunderstorm", provenance: str="SYNTHETIC") -> ImpactAssessment:
    distance=hypot(cell_xy[0]-district_xy[0],cell_xy[1]-district_xy[1])
    arrival=distance/speed_pixels_per_minute if speed_pixels_per_minute>0 else None
    level="SEVERE" if probability>=.8 else "HIGH" if probability>=.6 else "MODERATE" if probability>=.35 else "LOW"
    action=("Immediate shelter and district emergency review; issue NDMA-aligned precautions."
            if level in {"SEVERE","HIGH"} else "Monitor cell evolution and prepare local advisories.")
    return ImpactAssessment(district,hazard,float(probability),None if arrival is None else round(arrival,1),level,action,provenance)
