"""Quality control and registration checks before model fusion."""
from dataclasses import dataclass, asdict
from typing import Dict, Iterable
import numpy as np
@dataclass
class QCResult:
    source: str; passed: bool; missing_fraction: float; range_ok: bool; message: str
    def as_dict(self): return asdict(self)
def check_grid(source, values):
    a=np.asarray(values,dtype=float); missing=float(np.mean(~np.isfinite(a))) if a.size else 1.
    finite=a[np.isfinite(a)]; range_ok=bool(finite.size and np.nanmax(np.abs(finite))<1e6)
    passed=bool(a.ndim==2 and a.size and missing<=.25 and range_ok)
    return QCResult(source,passed,missing,range_ok,"ok" if passed else "rejected by shape/missing/range QC")
def qc_payload(groups):
    return [check_grid(source,obs.values) for group in groups for source,obs in group.items()]
def common_timestamp(groups):
    stamps=[obs.meta.timestamp_utc for group in groups for obs in group.values()]
    return min(stamps) if stamps else None
