# Earth Operations UI

The dashboard is an original operational weather-console interface inspired by the information architecture of professional nowcasting products.

Run:

```bash
uvicorn app.service:app --reload
streamlit run app/dashboard.py
```

The synthetic view provides an India-centered illustrative Earth projection and a globe toggle. It is explicitly labelled synthetic and does not claim real geolocation. Once `GridObservation` payloads contain authorized georeferenced radar/satellite/NWP data and lightning events, replace the demo coordinate projection with true geographic layers.
