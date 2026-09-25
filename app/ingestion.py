"""Provenance-aware, multi-source ingestion contracts and demo generator.

The generator is explicitly SYNTHETIC. Real adapters accept normalized records from
MOSDAC, GFS/ERA5, WWLLN/WGLC and ILLN without pretending network access exists.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Sequence
import numpy as np

SOURCES = ("MOSDAC_RADAR_1", "MOSDAC_RADAR_2", "MOSDAC_INSAT", "GFS_ERA5", "WWLLN_WGLC", "ILLN")

@dataclass(frozen=True)
class ProvenanceTag:
    value: str
    def __post_init__(self):
        if self.value not in {"LIVE", "SYNTHETIC"} and not self.value.startswith("REPLAY:"):
            raise ValueError("provenance must be LIVE, SYNTHETIC, or REPLAY:<case>")

@dataclass
class SensorRecord:
    timestamp: datetime
    source: str
    values: Dict[str, float]
    provenance: ProvenanceTag
    availability: str = "available"
    metadata: Dict[str, Any] = field(default_factory=dict)
    def as_dict(self) -> Dict[str, Any]:
        return {"timestamp": self.timestamp.isoformat(), "source": self.source,
                "values": self.values, "provenance": self.provenance.value,
                "availability": self.availability, "metadata": self.metadata}

class MultiSensorIngestor:
    """Normalize observations. No live feed is fabricated by this class."""
    def __init__(self, seed: int = 26072): self.rng = np.random.default_rng(seed)
    def ingest(self, records: Iterable[SensorRecord]) -> List[SensorRecord]: return list(records)
    def normalize_payload(self, payload: Mapping[str, Any], provenance: str) -> List[SensorRecord]:
        tag = ProvenanceTag(provenance); now = datetime.now(timezone.utc); result = []
        for source, values in payload.items():
            if source not in SOURCES: raise ValueError(f"unsupported source: {source}")
            result.append(SensorRecord(now, source, {str(k): float(v) for k, v in values.items()}, tag,
                                       metadata={"source_contract": source}))
        return result
    def synthetic_snapshot(self, cells: int = 4, provenance: str = "SYNTHETIC") -> List[SensorRecord]:
        if provenance != "SYNTHETIC": raise ValueError("synthetic_snapshot must be tagged SYNTHETIC")
        now = datetime.now(timezone.utc); rows = []
        for i in range(cells):
            growth = float(self.rng.normal(.5, .25)); cooling = float(self.rng.normal(-.6, .35))
            rows.append(SensorRecord(now, "SYNTHETIC_SCENARIO", {
                "cell_id": float(i), "vil": float(self.rng.uniform(15, 65)), "vil_trend": growth,
                "echo_top_km": float(self.rng.uniform(6, 15)), "echo_top_growth": float(abs(growth)),
                "brightness_temp_trend": cooling, "cape": float(self.rng.uniform(500, 3000)),
                "shear": float(self.rng.uniform(5, 30)), "flash": float(self.rng.random() < .18)},
                ProvenanceTag("SYNTHETIC"), metadata={"sources": ["synthetic_physics_calibration"]}))
        return rows
