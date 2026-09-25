"""Configuration and operational warning contracts."""
from pydantic import BaseModel, Field
from typing import Literal, Optional

Provenance = str
ForecastHorizon = Literal[5, 15, 30, 60, 180]

class RecordMeta(BaseModel):
    provenance: Provenance
    source: str
    case_id: Optional[str] = None
    timestamp_utc: Optional[str] = None
    note: Optional[str] = None

class WarningContext(BaseModel):
    district: str = "Unknown"
    state: str = "Unknown"
    ndma_actions: str = Field(default=(
        "Move indoors to a substantial shelter; avoid open fields, water, isolated trees, "
        "and metal objects; unplug sensitive equipment and follow local IMD/SDMA instructions."
    ))

class SensorHealth(BaseModel):
    source: str
    status: Literal["LIVE", "REPLAY", "SYNTHETIC", "DELAYED", "MISSING"]
    provenance: str
    latency_minutes: Optional[float] = None
