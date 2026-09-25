"""Typed, georeferenced observation contracts used by replay and live serving."""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

class GridMeta(BaseModel):
    timestamp_utc: datetime
    lat_min: float; lat_max: float; lon_min: float; lon_max: float
    ny: int = Field(gt=0); nx: int = Field(gt=0)
    crs: str = "EPSG:4326"
    resolution_km: Optional[float] = None

class GridObservation(BaseModel):
    source: str
    product: str
    provenance: str
    meta: GridMeta
    values: List[List[float]]

class LightningEvent(BaseModel):
    timestamp_utc: datetime
    latitude: float; longitude: float
    event_type: str = "flash"
    quality: Optional[float] = None
    source: str = "IITM_ILLN"
    provenance: str

class ReplayPayload(BaseModel):
    case_id: str
    provenance: str
    radar: Dict[str, GridObservation] = {}
    satellite: Dict[str, GridObservation] = {}
    nwp: Dict[str, GridObservation] = {}
    lightning: List[LightningEvent] = []

class NowcastRequest(BaseModel):
    provenance: str = "SYNTHETIC"
    case_id: Optional[str] = None
    district: str = "Unknown"; state: str = "Unknown"
    radar: Dict[str, GridObservation] = {}
    satellite: Dict[str, GridObservation] = {}
    nwp: Dict[str, GridObservation] = {}
    lightning: List[LightningEvent] = []
    radar_field: List[List[float]] = []
    flash: bool = False
