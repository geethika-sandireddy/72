from pydantic import BaseModel, Field
from typing import Literal, Optional

Provenance = Literal["LIVE", "REPLAY:CASE", "SYNTHETIC"]
ForecastHorizon = Literal[5, 15, 30, 60, 180]


class RecordMeta(BaseModel):
    provenance: Provenance
    source: str
    case_id: Optional[str] = None
    timestamp_utc: Optional[str] = None
    note: Optional[str] = None


class WarningContext(BaseModel):
    district: str
    state: str
    ndma_actions: str = Field(default="Move to a safe shelter; avoid open fields; do not stand under isolated tall objects.")
