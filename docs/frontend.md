# Frontend / operator-console notes

The Streamlit console is intentionally map-first and original. It is inspired by operational weather-console information architecture, not copied from any external repository.

Implemented in `app/dashboard.py`:

- Mission header and mode/provenance ribbon
- Full primary hazard workspace with selectable forecast horizon
- Storm-cell panel with intensity, area, movement and growth
- LAD state panel
- Multi-horizon timeline
- Source-health/evidence view
- Risk and NDMA action view
- Human reviewer workflow: approve, edit/hold, dismiss
- Explicit synthetic/replay/live gating
- Honest labels for grid fallback, uncalibrated uncertainty and missing geographic infrastructure data

The current backend provides a raster/grid fallback for synthetic mode, not georeferenced map tiles or real replay payloads. The UI therefore does not pretend the grid is a geographic map. Once `GridObservation` payloads with coordinates and authorized replay/live adapters are connected, the same workspace can render geographic layers.
