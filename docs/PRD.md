# PRD: VehicleGPT Edge

Status: v1.0 · Owner: Krish Jain and team · Competition: Tata Elxsi Teliport Season 4, Case Study 5

## 1. Summary
VehicleGPT Edge is an on-device vehicle assistant for software-defined vehicles. It continuously ingests vehicle signals, events and logs, keeps weeks of history locally, and does two things: it explains what changed before the user asks (proactive insights), and it answers natural-language questions about the vehicle's history (ask anytime). It runs without cloud, inside about 2 GB RAM and 2 ARM A5x-class cores, and has no way to write to the vehicle.

Core idea: deterministic code finds and measures; a 0.5 to 1.5B model only plans a query and explains verified evidence.

## 2. Problem
- Warning lights say what, never why. Finding the cause needs a workshop and a scan tool.
- Cloud assistants need connectivity and ship driving data out.
- Chatbots over raw logs guess and invent numbers.
- Vehicles produce vast data nobody reads. Service, fleet and validation teams lose hours digging through it.

## 3. Users and jobs
| User | Job to be done |
|---|---|
| Driver | Understand why something happened, in plain language, without being distracted. |
| Service engineer | Get likely causes and the signal timeline before touching the car. |
| Fleet operator | See exceptions across vehicles without raw data leaving them (R3). |
| Validation engineer | Ask plain-English questions over test drives; triage events automatically. |

## 4. Goals and non-goals
Goals
- G1 Proactive, evidence-backed explanations for events, drifts and trips.
- G2 Natural-language Q&A over at least 8 weeks of history (hot 15 min, warm 14 days at 1 Hz, cold 90 days rollups).
- G3 Fully offline; fits the budgets in section 8.
- G4 Safety isolation by construction and by test.
- G5 Reproducible demo: scenarios with ground truth, golden questions, benchmarks.

Non-goals (this release)
- Real vehicle integration, AUTOSAR/ASIL certification, Android Automotive app, CARLA by default, fleet cloud backends, OTA, multi-vehicle, training a model from scratch.

## 5. Product principles
1. The car speaks first, and you can always ask.
2. Every claim cites a signal and a time. Unverified numbers are blocked.
3. Quiet by default: non-urgent messages wait until you park.
4. Advisory only. Native warnings are first-line.
5. Works with no model attached (templates). The model improves wording.

## 6. Release scope
- R1 (Round 2 demo): milestones M0 to M8. Simulator, ingest, store, insight engine, ask engine, API, IVI + service UI, benchmarks, Docker, `a55` profile.
- R2 (hardening): M9 items: CARLA bridge, Cuttlefish VHAL, vsomeip, voice, SQLCipher, block-compressed warm tier, Rust ingest, fleet digest.
- R3 (production path): HPC profile, multi-vehicle fleet sync, ECU-side adapters, security review.

## 7. Functional requirements
Priority: M = must (R1), S = should, C = could.

### 7.1 Simulation and data (FR-S)
- FR-S1 (M) Scenario engine: YAML scenario to physics-based vehicle model to signals. Deterministic per seed. AC: `demo_21d` backfills 21 days in under 10 minutes on a laptop.
- FR-S2 (M) Live mode at 1x and Nx speed feeding CAN transport and UDP adapters (SOME/IP-mock, VHAL-mock, QNX log lines, UDS DTC records). AC: at 1x, three sources ingest concurrently with under 1% loss.
- FR-S3 (M) Fault injection: `cell_overtemp`, `tyre_leak`, `lane_marking_fade`, `sensor_loss`, `regen_limit_change`, `dtc_set`.
- FR-S4 (M) Ground truth JSON emitted with every backfill (events, contributor shares, change-points, trip splits).
- FR-S5 (S) Replay recorded ASC/BLF logs through the same pipeline.
- FR-S6 (C) CARLA bridge adapter.

### 7.2 Ingest (FR-I)
- FR-I1 (M) Decode CAN/CAN-FD frames via DBC into canonical samples.
- FR-I2 (M) Adapters for SOME/IP-mock, VHAL-mock, QNX logs, UDS; one canonical schema `(vehicle_id, ts_ms, signal, value, quality)`.
- FR-I3 (M) Tolerate drops, duplicates and out-of-order frames; drop-oldest backpressure on the hot buffer.
- FR-I4 (M) Read-only guard: `ReadOnlyBus` raises on any send. AC: safety test passes.

### 7.3 Storage (FR-D)
- FR-D1 (M) Tiers: hot ring (15 min raw), warm (14 days, deadband + heartbeat), cold (90 days, 1-minute rollups), event black-box (plus/minus 60 s at full resolution per event).
- FR-D2 (M) Retention job: oldest-first purge, black-box windows protected, runs while parked.
- FR-D3 (M) FTS5 index over DTC text, warn+ log lines and insight text.
- FR-D4 (S) Size report endpoint. AC: 21 days of the 35-signal catalogue under 400 MB warm, 250 MB cold.

### 7.4 Insight engine (FR-N)
- FR-N1 (M) Detectors: limit, rate-of-rise, DTC/ADAS passthrough (event); robust z-score and CUSUM (drift); change-point on daily efficiency.
- FR-N2 (M) Evidence pack per insight: window, facts, ranked contributors against a baseline, references.
- FR-N3 (M) Insight kinds: EVENT_EXPLANATION, DRIFT, TRIP_SUMMARY, CASE_FILE.
- FR-N4 (M) Delivery policy: severity tiers, driving/parked/charging state, dedup, daily budget, dismissal suppression.
- FR-N5 (M) Template narration within 2 s of an event; model narration within 20 s, cached.
- FR-N6 (S) Nightly drift scan when parked.

### 7.5 Ask engine (FR-A)
- FR-A1 (M) Router: rules + embedding exemplars to an intent; skips the LLM for common intents.
- FR-A2 (M) Planner: SLM to JSON query plan via grammar; relative time resolved by code.
- FR-A3 (M) Tools: trend, driver decomposition, change-point, events, pre-event scan, compare segments, trip summary, point lookup.
- FR-A4 (M) Answer card first (numbers + chart spec), then streamed narration, then `verified` flag.
- FR-A5 (M) Verifier: every number and time in narration must match facts; regenerate once; then template.
- FR-A6 (M) Follow-up context: "Why?" on an insight passes `insight_id`; last turn remembered.
- FR-A7 (M) Out-of-scope questions answered with a clear "I can't answer that from vehicle data".

### 7.6 API (FR-P)
- FR-P1 (M) REST + SSE + WebSocket per `docs/API_SPEC.md`. FR-P2 (M) Role tokens: driver, service. FR-P3 (S) Dev-only sim control routes.

### 7.7 UI (FR-U)
- FR-U1 (M) IVI screen: since-you-parked feed, explanation panel, ask panel, parked/driving/charging modes.
- FR-U2 (M) Service UI: events table, event detail with timeline chart, auto case file, export.
- FR-U3 (M) Every state in `docs/UX_SPEC.md` implemented: loading, empty, error, offline model, verifier fallback.
- FR-U4 (S) Fleet and validation digest page.
- FR-U5 (C) Local voice in and out.

### 7.8 Ops (FR-O)
- FR-O1 (M) Profiles `dev`, `a55`, `hpc` via `VGPT_PROFILE`. FR-O2 (M) Docker Compose with resource caps (core 450 MB, llm 900 MB, 2 CPUs total for the `a55` bench). FR-O3 (M) `/v1/health` and a metrics panel (RSS, p50/p95 latency, queue depth). FR-O4 (S) arm64 images; QEMU nightly run.

## 8. Non-functional requirements (design targets, validated in M8)
| ID | Requirement | Target |
|---|---|---|
| NFR-1 | Answer card, common queries, `a55` profile | p95 < 1 s |
| NFR-2 | First narrated token | p95 < 2 s |
| NFR-3 | Event to template insight / model-narrated insight | < 2 s / < 20 s |
| NFR-4 | Core RSS / llm RSS (0.5B) / total incl. OS and excluding web UI and sim | 450 MB / 600 MB / 1.2 GB |
| NFR-5 | Startup to ready | < 30 s |
| NFR-6 | Network egress from core | zero |
| NFR-7 | Intent accuracy and evidence match on the golden set | at least 95% |
| NFR-8 | Verifier escapes (unverified number shown as verified) | 0 |
| NFR-9 | False critical alerts on `clean_21d` / false advisory per week | 0 / at most 1 |
| NFR-10 | Searchable history | at least 8 weeks (14 d warm + 90 d cold) |

## 9. Demo script (6 minutes, offline)
1. `make demo`; 21 days of history load; show the resource panel.
2. Live sim is parked and charging. A fast-charge session heats the pack; the IVI shows "Battery heated up 11 °C in 8 minutes" with ranked contributors.
3. Press Why. Ask "Is this normal for fast charging?" Answer card under 1 s, then verified narration.
4. Ask the five brief questions: range drop, efficiency drop, ADAS disengagements yesterday, before the overheating warning, city vs highway.
5. Service UI: auto case file for the event; export.
6. Safety: attempt a bus write from the AI side; show it blocked. Show zero outbound traffic.
7. Switch to the `a55` profile (2 CPUs, 2 GB container) and repeat one query with the latency shown.

## 10. Success metrics
Demo runs offline without intervention; all NFR gates met or honestly reported; golden set at least 95%; judges can see cause, evidence and isolation in under 3 minutes.

## 11. Risks
| Risk | Mitigation |
|---|---|
| Model too slow on A55-class CPU | Fast path skips the LLM; answer card before narration; 0.5B profile; template fallback. |
| Hallucinated numbers | Verifier + facts-only prompts + fallback. |
| Storage growth | Deadband + heartbeat, rollups, retention, size report. |
| Scope creep | Milestone gating; M9 is optional. |
| Simulator realism questioned | Ground truth published; physics parameters documented; replay adapter for real logs. |
| Dev machines lack vcan | `udp_multicast` transport default off Linux. |
| IP terms | Check Round 2 terms before open-sourcing. |

## 12. Open questions
1. Real hardware for the demo (Pi 5 + AI HAT, or container only)? 2. Vehicle type for the main demo (EV default; add fuel signals for ICE)? 3. Which Round 2 deliverable format (video, repo, live demo)?

## 13. Traceability to the brief
| Brief item | Where |
|---|---|
| High-level architecture; edge deployment | ARCHITECTURE, FR-O |
| Vehicle data collection (CAN, SOME/IP, VHAL, QNX, ADAS, camera, diagnostics) | FR-I, DATA_MODEL, SIMULATION |
| Scenario recreation (CARLA or simulated/recorded) | FR-S, SIMULATION |
| SLM/LLM selection rationale | AI_PIPELINE, DECISIONS D4/D5 |
| Search and retrieval workflow | FR-A, AI_PIPELINE |
| Historical storage, weeks searchable | FR-D, DATA_MODEL |
| User interaction design | FR-U, UX_SPEC |
| Isolation of safety-critical functions | FR-I4, SAFETY_SECURITY |
| Memory, latency, scalability, privacy | NFR, TEST_PLAN |
