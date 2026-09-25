# Official data strategy for SIH 2026 PS 26072

This repository now treats the following as the official first-pass source stack for the thunderstorm and lightning nowcasting prototype.

## 1) Decision summary

We are not treating all weather products as equivalent. The correct design is:

- Radar: IMD Doppler Weather Radar (DWR) network
- Satellite: INSAT-3D / INSAT-3DR / INSAT-3DS satellite products via MOSDAC and IMD SATMET workflows
- Lightning: IITM / IMD lightning network observations, especially the Indian Lightning Location Network (ILLN) and IMD-integrated lightning product layers
- NWP/model: short-range Indian operational models first (IMD HRRR, IMD EWRF, WRF, BharatFS / NCUM-family), with ERA5 and NOAA GFS as open historical/training backups

This is the correct operational framing for a disaster-management and nowcasting system over India.

## 2) Why this is the correct source stack

The PS is explicit: multi-source nowcasting that combines radar, satellite, lightning and model information. The official Indian meteorological ecosystem already organizes these sources as separate but complementary observation/model families.

- IMD radar provides the storm structure and motion signal
- INSAT provides cloud structure, thermal/top-of-cloud signatures, moisture and motion proxies
- Lightning observations capture actual deep-convective electrical activity
- NWP provides the thermodynamic and dynamic environment that can support or suppress convection

## 3) Core official source stack

### 3.1 Radar: IMD DWR

Primary choice:
- IMD Doppler Weather Radar network
- Hyderabad DWR is a relevant station for prototype regional case studies

Recommended products:
- Base reflectivity / PPI-Z
- Max reflectivity / MAX-Z
- Radial velocity / PPI-V
- Surface rainfall intensity / SRI
- Optional: VVP and other derived wind products

Why:
- This is the main observation stream for storm intensity, morphology and motion
- It is the most directly relevant data source for nowcasting and severe thunderstorm detection in India

### 3.2 Satellite: MOSDAC + INSAT

Primary choice:
- INSAT-3D / INSAT-3DR / INSAT-3DS data products via MOSDAC and IMD SATMET archives

Recommended products:
- Thermal IR (TIR-1 / TIR-2)
- Water vapour (WV)
- Cloud motion vectors (CMV / AMV)
- Upper tropospheric humidity (UTH)
- Quantitative precipitation estimation / rainfall products (QPE / IMR where available)
- Visible and short-wave / mid-wave IR as supplemental channels for daylight cases

Why:
- Cloud-top temperature, moisture and cloud motion are highly informative for deep convection and severe weather evolution
- These are official Indian meteorological products and are consistent with the PS requirement for satellite ingestion

### 3.3 Lightning: IITM / IMD lightning network

Primary choice:
- IITM Indian Lightning Location Network (ILLN)
- IMD-integrated lightning product layers where available

Recommended features:
- Flash locations
- Flash counts in rolling windows: 5, 10, 15, 30, 60 min
- Flash density fields
- Flash-rate jumps and temporal trends

Why:
- Lightning is a direct electrical indicator of thunderstorm severity and should be modeled as a distinct output channel, not hidden inside the radar stream
- This is the most direct way to satisfy the PS requirement that thunderstorm and lightning be treated separately

### 3.4 NWP / model: IMD and NCMRWF ecosystems

Primary model choices:
- IMD HRRR or very-short-range high-resolution NWP, if available through operational channels
- IMD EWRF / WRF-based short-range forecast products
- BharatFS / NCUM / NCUM-R for wider atmospheric context

Recommended variables:
- Temperature
- Relative humidity
- Wind u/v
- Pressure
- Precipitation / rainfall accumulation
- CAPE / CIN / lifted index / K-index / total totals
- Vertical velocity
- Wind shear
- Moisture-related variables

Why:
- Short-range convective support is more relevant than generic long-range global models for nowcasting
- IMD explicitly documents short-range meteorological systems relevant to thunderstorm and lightning forecasting

## 4) Official historical training backups

These are not the primary operational live stack, but they are important for historical training and reproducible evaluation.

### 4.1 ERA5

Use when historical atmospheric coverage is needed and operational model archives are not available.

- Real historical atmospheric reanalysis
- Excellent for atmospheric-state context and feature engineering
- Not a real-time forecast product; it is a reanalysis product
- Best used as an atmospheric context source, not as a replacement for IMD operational model data

### 4.2 NOAA GFS

Use as an open public forecast backup when historical operational Indian forecast fields are not easily accessible.

- Publicly accessible GRIB2 archive
- Great for reproducible open-data experimentation
- Not equivalent to IMD BharatFS / NCUM / HRRR / EWRF

## 5) Recommended data strategy for the prototype

### Live operational path

- Radar: IMD DWR latest product stream
- Satellite: MOSDAC INSAT near-real-time archive / current product feed
- Lightning: IITM / IMD lightning product feed
- Model: IMD HRRR / EWRF / BharatFS / NCUM, depending what is available operationally

### Training and replay path

- Historical radar products from IMD DWR archive
- Historical INSAT archive from MOSDAC
- Historical lightning records from IITM/IMD archived observations
- Historical NWP fields from Indian operational archives when available
- ERA5 / NOAA GFS as open fallback for atmospheric context if the Indian archive is incomplete

## 6) Time alignment and preprocessing design

The critical point is that these sources do not update at the same rate or resolution.

To make the ML pipeline valid, we need a single synchronization layer:

1. Quality control
2. Temporal alignment to a master timestamp (e.g. 10–15 min grid)
3. Spatial alignment and regridding onto a common India domain / district grid
4. Weather feature extraction
5. Event labeling for training

We do not build a single raw merge of files; we build a synchronized observation tensor.

## 7) Recommended initial dataset scope for the prototype

For the first credible prototype, use a manageable multi-source set rather than every product under the sun.

### Radar
- PPI-Z / reflectivity
- MAX-Z
- PPI-V

### Satellite
- TIR-1 / TIR-2
- WV
- CMV / AMV
- QPE / rainfall estimate (optional)

### Lightning
- Flash locations and rolling counts from IITM / IMD

### NWP
- Temperature, RH, wind U/V, CAPE/CIN, vertical velocity, moisture and convective indices

That gives a strong but tractable feature set.

## 8) Recommended official data lake design

Use the following data categories:

- `radar/<station>/<product>/<yyyy>/<mm>/<dd>/...`
- `satellite/insat/<product>/<yyyy>/<mm>/<dd>/...`
- `lightning/<source>/<yyyy>/<mm>/<dd>/...`
- `nwp/<model>/<variable>/<yyyy>/<mm>/<dd>/...`
- `labels/<case_id>/...`

Each record must carry:
- timestamp_utc
- source
- provenance (`LIVE`, `REPLAY:<case>`, `SYNTHETIC`)
- product/version metadata
- quality flags

## 9) Decision: what we should code as the first data system

The repository should reflect the following decisions in code and documentation:

- official data inventory modules
- official source contract definitions
- explicit separation between operational and fallback training data
- no claim that synthetic data is real
- no mixing of random open weather APIs into the official pipeline

This is the first engineering step before any serious model training.

## 10) Final recommendation

For PS 26072, lock the source stack as:

- Radar: IMD DWR
- Satellite: INSAT-3D / 3DR / 3DS via MOSDAC + IMD
- Lightning: IITM / IMD lightning network
- NWP / model: IMD HRRR, EWRF, BharatFS / NCUM-family
- Historical atmospheric backup: ERA5 and NOAA GFS

This is the cleanest, most defensible first-pass architecture for a real Indian thunderstorm/lightning nowcasting system.
