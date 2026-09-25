"""Operational targets and labels; definitions are explicit and reproducible."""
from dataclasses import dataclass
from typing import Iterable
import numpy as np
@dataclass(frozen=True)
class TargetDefinition:
    lightning: str="at least one quality-approved flash in the future grid/window"
    thunderstorm: str="future radar cell with max reflectivity >= 40 dBZ and area >= 3 pixels"
    horizons: tuple=(5,15,30,60,180)
def lightning_target(events, meta, minutes):
    return int(any(0 <= (e.timestamp_utc-meta.timestamp_utc).total_seconds()/60 <= minutes for e in events))
def thunderstorm_target(future_field, threshold=40., min_area=3):
    a=np.asarray(future_field,float); return int(np.sum(a>=threshold)>=min_area)
