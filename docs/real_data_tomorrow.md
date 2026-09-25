# Real-data emergency plan for tomorrow's presentation

## Recommended source: SEVIR public benchmark

SEVIR provides real storm-event sequences containing NEXRAD radar-derived VIL, GOES satellite imagery, and GOES GLM lightning observations in a public AWS bucket. It is a US benchmark, not Indian data. Use it to demonstrate that the temporal multi-modal pipeline works, but state clearly that it is **cross-domain benchmark evidence**, not India operational validation.

### Inspect public data without credentials

```bash
python scripts/fetch_sevir_sample.py --prefix data/
```

The command only lists the selected public prefix first, so you can avoid downloading the ~large full archive accidentally. After inspecting the listing, sync a deliberately small prefix:

```bash
python scripts/fetch_sevir_sample.py --sync-mode --prefix <small-selected-prefix>
```

Register a selected event as a replay case:

```bash
python scripts/register_sevir_case.py sevir-demo-001
python scripts/validate_replay.py data/replay
```

## What to say to NTRO

> We use an openly accessible real-storm benchmark to validate the end-to-end temporal pipeline and compare against persistence/advection. Indian deployment remains a separate domain-transfer step because radar/satellite geometry and storm climatology differ.

Do **not** call SEVIR an Indian dataset, do not claim IMD performance from it, and do not present the registration template as a completed evaluation. Only show scores after the selected event arrays and labels have actually been mapped into the replay bundle.

## Faster presentation strategy

1. Run the synthetic Earth console for the polished India operator workflow.
2. Show the SEVIR public-benchmark ingestion command and provenance panel.
3. Show the baseline benchmark report only if real selected-event arrays are present.
4. Explain the domain-shift guard as a strength: the system refuses to turn US benchmark skill into an India claim.

Useful public references:

- SEVIR registry: https://registry.opendata.aws/sevir/
- SEVIR challenge code: https://github.com/MIT-AI-Accelerator/sevir_challenges
- Public data bucket: `s3://sevir/`
- India-facing sources to connect later: https://www.mosdac.gov.in/opendata and https://mausam.imd.gov.in/
