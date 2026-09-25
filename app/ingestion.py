"""Provenance-first sensor records and deterministic synthetic fallback."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List
import numpy as np

VALID_PROVENANCE = {"LIVE", "SYNTHETIC"}

@dataclass(frozen=True)
class ProvenanceTag:
    kind: str
    case_id: str | None = None
    def __post_init__(self):
        if self.kind not in VALID_PROVENANCE and not self.kind.startswith("REPLAY:"):
            raise ValueError(f"Unsupported provenance: {self.kind}")
    @property
    def value(self) -> str:
        return self.kind if self.case_id is None else f"{self.kind}:{self.case_id}"

@dataclass
class SensorRecord:
    timestamp: datetime
    source: str
    values: Dict[str, float]
    provenance: ProvenanceTag
    metadata: Dict[str, Any] = field(default_factory=dict)
    def as_dict(self) -> Dict[str, Any]:
        return {"timestamp": self.timestamp.isoformat(), "source": self.source,
                "values": self.values, "provenance": self.provenance.value,
                "metadata": self.metadata}

class MultiSensorIngestor:
    """Adapter boundary for MOSDAC, GFS/ERA5 and WWLLN/ILLN-compatible feeds."""
    SOURCES = ("MOSDAC_RADAR", "MOSDAC_INSAT", "GFS_ERA5", "WWLLN_WGLC", "ILLN")
    def __init__(self, seed: int = 26072):
        self.rng = np.random.default_rng(seed)
    def synthetic_snapshot(self, cells: int = 4, provenance: str = "SYNTHETIC") -> List[SensorRecord]:
        now = datetime.now(timezone.utc)
        records = []
        for i in range(cells):
            records.append(SensorRecord(now, "MULTI_SENSOR", {
                "cell_id": float(i), "vil": float(self.rng.uniform(15, 65)),
                "vil_trend": float(self.rng.normal(0.4, 0.3)),
                "echo_top_km": float(self.rng.uniform(6, 15)),
                "echo_top_growth": float(self.rng.normal(0.1, 0.15)),
                "brightness_temp_trend": float(self.rng.normal(-0.4, 0.5)),
                "cape": float(self.rng.uniform(500, 3000)),
                "shear": float(self.rng.uniform(5, 30)),
                "flash": float(self.rng.random() < 0.18),
            }, ProvenanceTag(provenance), {"sources": list(self.SOURCES)}))
        return records
    def ingest(self, records: Iterable[SensorRecord]) -> List[SensorRecord]:
        return list(records)
