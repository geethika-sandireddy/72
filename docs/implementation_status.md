# SIH 2026 PS 26072 — Current implementation status

## Implemented architecture

- Typed geospatial observation contracts for radar, satellite, lightning events and NWP
- Provenance enforcement for `LIVE`, `REPLAY:<case-id>`, and `SYNTHETIC`
- Separate modality encoders and evidence-aware availability/agreement metadata
- QC helpers, lightning-jump and storm-motion descriptors
- Persistent case state for storm-cell/LAD evolution
- Independent lightning and thunderstorm target definitions and model-head infrastructure
- Rare-event metrics and baseline/ablation utilities
- Spatial field and impact/arrival-time interfaces
- Replay manifest validator and tamper-evident audit records

## What is deliberately not claimed

The repository does not claim real-data forecast skill until authorized historical case data are placed under `data/replay/`, validated, trained, and evaluated on disjoint storm cases. The checked-in demo is synthetic and must remain labelled `SYNTHETIC`.

## Adding an authorized replay case

1. Copy the layout described in `data/replay/README.md`.
2. Replace `_metadata.template.json` with `<case-id>/metadata.json`.
3. Add the authorized files and preserve source timestamps, product names, quality flags, and licensing notes.
4. Run:

```bash
python scripts/validate_replay.py data/replay
pytest -q
```

5. Only after validation should a training/evaluation job consume the case. Split complete storm cases—not individual frames—between train, validation and test.

This is the correct next step for legitimate hackathon data; the repository will not invent files or silently relabel synthetic data.
