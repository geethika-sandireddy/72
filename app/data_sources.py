"""Official-source data contracts for SIH PS 26072.

This module is intentionally opinionated and operationally grounded:
- IMD DWR is the primary radar source
- INSAT from MOSDAC/IMD is the primary satellite source
- IITM/IMD lightning is the primary lightning source
- short-range operational models (HRRR/EWRF/BharatFS/NCUM-family) are the primary NWP pathway
- ERA5 and NOAA GFS are explicit training/fallback backups, not the main live system
"""
from dataclasses import dataclass
from typing import Literal, Optional

SourceCategory = Literal["RADAR", "SATELLITE", "LIGHTNING", "NWP", "REANALYSIS", "FALLBACK"]
Provenance = Literal["LIVE", "REPLAY:CASE", "SYNTHETIC"]

@dataclass(frozen=True)
class OfficialSource:
    category: SourceCategory
    name: str
    provider: str
    official_notes: str
    live_supported: bool
    historical_supported: bool
    recommended_for: str

OFFICIAL_SOURCES = {
    "IMD_DWR": OfficialSource(
        category="RADAR",
        name="IMD Doppler Weather Radar",
        provider="IMD",
        official_notes="Primary Indian radar source for storm intensity, motion, and precipitation structure.",
        live_supported=True,
        historical_supported=True,
        recommended_for="storm nowcasting and radar feature extraction",
    ),
    "MOSDAC_INSAT_3D": OfficialSource(
        category="SATELLITE",
        name="INSAT-3D / 3DR / 3DS products via MOSDAC",
        provider="ISRO / MOSDAC / IMD",
        official_notes="Official meteorological satellite imagery and derived products for cloud and atmospheric structure.",
        live_supported=True,
        historical_supported=True,
        recommended_for="cloud-top temperature, cloud motion, moisture, operational satellite features",
    ),
    "IITM_ILLN": OfficialSource(
        category="LIGHTNING",
        name="IITM Indian Lightning Location Network",
        provider="IITM / IMD",
        official_notes="Ground-based lightning observations and regional lightning activity tracking.",
        live_supported=True,
        historical_supported=True,
        recommended_for="lightning occurrence, flash-rate features, lightning target building",
    ),
    "IMD_HRRR": OfficialSource(
        category="NWP",
        name="IMD HRRR / very-short-range operational model",
        provider="IMD",
        official_notes="Very-short-range operational model support for nowcasting and storm development.",
        live_supported=True,
        historical_supported=True,
        recommended_for="very-short-range convective environment and nowcasting guidance",
    ),
    "IMD_EWRF": OfficialSource(
        category="NWP",
        name="IMD EWRF / short-range model",
        provider="IMD",
        official_notes="Short-range high-resolution model with strong relevance to lightning-convective forecasting.",
        live_supported=True,
        historical_supported=True,
        recommended_for="convective support and lightning-sensitive short-range forecast fields",
    ),
    "BharatFS": OfficialSource(
        category="NWP",
        name="Bharat Forecast System",
        provider="IMD",
        official_notes="Current operational Indian forecast system covering larger atmospheric context.",
        live_supported=True,
        historical_supported=True,
        recommended_for="regional and broader atmospheric context",
    ),
    "NCUM": OfficialSource(
        category="NWP",
        name="NCUM / NCUM-R",
        provider="NCMRWF",
        official_notes="Regional and global NCMRWF forecast systems used for atmospheric context and medium-range support.",
        live_supported=True,
        historical_supported=True,
        recommended_for="broad forecast environment and atmospheric support fields",
    ),
    "ERA5": OfficialSource(
        category="REANALYSIS",
        name="ECMWF ERA5",
        provider="ECMWF",
        official_notes="Historical atmospheric reanalysis and open benchmark data source for training and fallback feature generation.",
        live_supported=False,
        historical_supported=True,
        recommended_for="historical atmospheric context and training fallback",
    ),
    "NOAA_GFS": OfficialSource(
        category="FALLBACK",
        name="NOAA GFS",
        provider="NOAA / NCEP",
        official_notes="Public open forecast archive when operational Indian model archives are unavailable.",
        live_supported=True,
        historical_supported=True,
        recommended_for="open-source forecast fallback and reproducible validation",
    ),
}

CORE_LIVE_STACK = [
    "IMD_DWR",
    "MOSDAC_INSAT_3D",
    "IITM_ILLN",
    "IMD_HRRR",
    "IMD_EWRF",
]

CORE_TRAINING_STACK = [
    "IMD_DWR",
    "MOSDAC_INSAT_3D",
    "IITM_ILLN",
    "ERA5",
    "NOAA_GFS",
]

CORE_MODEL_FEATURES = {
    "radar": ["reflectivity", "max_reflectivity", "velocity", "rainfall_intensity"],
    "satellite": ["thermal_ir", "water_vapour", "cloud_motion_vector", "upper_tropospheric_humidity"],
    "lightning": ["flash_count_5m", "flash_count_15m", "flash_count_30m", "flash_count_60m"],
    "nwp": ["temperature", "relative_humidity", "wind_u", "wind_v", "cape", "cin", "vertical_velocity", "wind_shear"],
}
