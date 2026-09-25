# SIH 2026 PS 26072 — Thunderstorm & Lightning Nowcasting Prototype

This repository contains a fast prototype for an India-focused thunderstorm and lightning nowcasting system aligned to SIH 2026 PS 26072 (MoES/IMD, Disaster Management theme).

The implementation is intentionally scoped to a credible, testable prototype that can be executed in a short time window while still covering the required architecture and evaluation logic.

## Scope covered

- Core LAD (Leaky Accumulate-Discharge) cell with inspectable state
- Separate storm-cell tracking module
- Multi-horizon lightning/thunderstorm forecast heads at 5, 15, 30, 60, and 180 minutes
- Provenance tagging for every record: LIVE / REPLAY:<case-study> / SYNTHETIC
- Rare-event verification metrics: POD, FAR, CSI/ETS, Brier score, lead-time skill curve
- Leakage-safe train/test split logic
- Serving API and optional dashboard
- Synthetic fallback for lightning live-feed when ILLN bulk API is unavailable

## Required data sources

- NWP: NOAA GFS / ECMWF ERA5 (open, real data from day one)
- Satellite + radar: MOSDAC / ISRO SAC catalog (insights and registration path documented)
- Lightning climatology: WWLLN Global Lightning Climatology (open)
- Live lightning: India ILLN (bulk access may be unavailable; synthetic fallback is labeled SYNTHETIC)

## Repository structure

- `app/provenance.py` — provenance enums and record tagging
- `app/storm_cells.py` — connected-component tracker and per-cell features
- `app/lad_model.py` — LAD module and forecast head
- `app/metrics.py` — deterministic verification metrics and leakage checks
- `app/ingestion.py` — ingestion interfaces, multi-source data model, synthetic live lightning generator
- `app/service.py` — FastAPI serving layer with latency logging
- `app/dashboard.py` — streamlit dashboard, built after verification logic is working

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.service
```

Then visit:

- API: `http://localhost:8000/docs`
- Dashboard: `streamlit run app/dashboard.py`

## Operational notes

- No synthetic data is ever presented as real.
- The dashboard is intentionally written after the verification and serving logic.
- The prototype emphasizes interpretable, plottable storm state variables rather than opaque black-box predictions.
- Performance checks avoid temporal leakage by ensuring no case appears in both train and test splits.

## PS coverage summary

This prototype is designed to satisfy the explicit PS clauses:

- AIML-based nowcasting system
- Nowcasting horizon 5–180 minutes
- Separate thunderstorm and lightning output
- Multi-radar + satellite + lightning + NWP ingestion
- Inspectable LAD cell state `P_t`
- Storm-cell identification/tracking output as a separate deliverable
- Provenance tagging everywhere
- Rare-event verification metrics
- API + dashboard serving architecture
- Extra options included: action text, explainability panel, confidence intervals, replay tool

## Important caveat

This is a prototype, not a production operational forecasting system. It is designed to be credible, reproducible, and demonstrable within a short development window with real data hooks and explicit synthetic fallback labeling.
