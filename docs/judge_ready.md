# INDRA — judge-ready build notes

## What is now productized

INDRA is presented as a **reliability-aware convective intelligence console**, not a generic weather dashboard. The operator flow is:

```text
observation provenance
  → source health + freshness
  → QC / evidence separation
  → storm object + LAD state
  → separate lightning and thunderstorm horizons
  → spatial risk field
  → human review / decision support
  → auditable verification
```

The UI and API explicitly distinguish:

- `SYNTHETIC`: deterministic demonstration only
- `REPLAY:<case-id>`: authorized historical data only
- `LIVE`: actual source payload required

## The demonstration that should win attention

1. Start with the Earth Operations console.
2. Select a horizon and click the storm object.
3. Explain the hazard through **three independent views**: cell dynamics, LAD pressure, and source evidence.
4. Disable/delay one source and show `MISSING`/`DELAYED` plus an uncertainty warning.
5. Use the forecaster desk to record a review decision; emphasize that the prototype never claims to issue an official warning.
6. Switch to replay only when a validated authorized case exists, then show held-out metrics and baseline comparison.

## Non-negotiable presentation rules

Never say “real-time”, “calibrated”, “operational skill”, “India-wide validation”, or “official warning” unless the corresponding evidence is in the replay manifest and evaluation artifact.

The strongest defensible claim today is:

> INDRA is an auditable, provenance-first prototype for reliability-aware thunderstorm and lightning nowcasting, with an Earth-centered operator workflow and a clean path to authorized replay validation.

## Run

```bash
pip install -r requirements.txt
uvicorn app.service:app --reload
streamlit run app/dashboard.py
pytest -q
```
