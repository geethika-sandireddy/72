# INDRA Frontend

This directory contains the new premium operations-console frontend. It is a static frontend so it can be opened immediately without a Node toolchain:

```bash
cd frontend
python -m http.server 3000
```

Open http://localhost:3000.

The interface is intentionally original and does not copy the reference repository. It is a high-fidelity operational shell for the existing FastAPI/Streamlit prototype. The visible default state is explicitly `SYNTHETIC DEMO`; no values are presented as live observations.

The next integration step is wiring `frontend/app.js` to `POST /forecast` and mapping real `GridObservation.meta` bounds into the map layer. Until that is connected, this page is a deterministic presentation/demo surface, not a live weather product.
