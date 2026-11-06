---
name: add-detector
description: Add a new event or drift detector to the insight engine with tests, evidence contributors and templates. Use when asked to detect a new vehicle condition (for example 12 V sag, cell imbalance, tyre leak).
---
# Add a detector

1. Read `docs/DATA_MODEL.md` (signals, baselines) and `docs/AI_PIPELINE.md` section 5 (evidence pack).
2. Decide the type: event detector (`Detector.on_sample`) for thresholds, rates and passthroughs; scan detector (`ScanDetector.scan`) for drift, run while parked.
3. Create `vgpt/insight/detectors/<name>.py` implementing the Protocol in `vgpt/insight/base.py`. Use signal names from the catalogue only. Carry units in names. Use the clock abstraction.
4. Emit `EventCandidate(type, severity, subject, ts_ms, payload)`. Choose severity by `docs/PRD.md` rules: info, advisory, warning, critical. Never emit critical unless a native warning or DTC exists.
5. Register the detector in `vgpt/insight/registry.py` with config (thresholds, window, cooldown) in `signals.yaml` or `detectors.yaml`, not in code.
6. Evidence: add contributor candidates (signals worth ranking for this event) to `vgpt/insight/contributors.py`; ensure baselines exist for the vehicle state involved.
7. Template: add a narration template in `vgpt/insight/narrate_templates.py` using only evidence facts; plain words; no imperative safety instructions.
8. Tests (write first): unit tests with synthetic series (fires, does not fire, cooldown, noise); integration test with a scenario injector in `vgpt/sim`; add the new injector and ground-truth entry if needed; run `clean_21d` to confirm no false alerts.
9. Run `make test lint safety`. Update `docs/DATA_MODEL.md` if a signal or event type was added.
