# Tasks and milestones

Work one milestone at a time. Tick boxes only when `make test lint safety` pass. At each gate, stop and show the human the demo or report.

## Status log
| Date | Milestone | Note |
|---|---|---|
| | | |

## M0 Bootstrap
- [ ] M0.1 Repo layout from `AGENTS.md`; `pyproject.toml` (uv), ruff, mypy strict, pytest, pre-commit
- [ ] M0.2 `vgpt.common`: `Settings`, `clock` (wall and sim), ids, units, logging without PII
- [ ] M0.3 `Makefile` targets: setup, test, lint, demo, bench, safety
- [ ] M0.4 `docker-compose.yml` skeleton (sim, core, llm, web) with caps; `scripts/fetch_models.sh` (Qwen2.5 0.5B and 1.5B GGUF)
- [ ] M0.5 GitHub Actions: lint, test, safety
- [ ] M0.6 `apps/web` Next.js skeleton, Tailwind tokens from `UX_SPEC.md`, self-hosted Barlow
Gate: `make setup test lint safety` green on a clean clone; `docker compose config` valid.

## M1 Schema and store
- [ ] M1.1 Pydantic records, signal catalogue loader (`signals.yaml` from `DATA_MODEL.md`)
- [ ] M1.2 `Store` Protocol; `SqliteStore` with the DDL, pragmas, migrations
- [ ] M1.3 `HotBuffer` ring; deadband and heartbeat writer; 1-minute rollups
- [ ] M1.4 Black-box snapshot (pre and post window); FTS5 indexing and search
- [ ] M1.5 Retention job; `size_report`
- [ ] M1.6 Tests: write/read round trip, forward-fill, rollup correctness, purge keeps black-box, concurrent reader during writes
Gate: store benchmark script writes 35 signals x 1 day in under 60 s and reports size.

## M2 Simulator
- [ ] M2.1 Vehicle model per `SIMULATION.md` with params file; deterministic RNG
- [ ] M2.2 Scenario loader and fault injectors (six types)
- [ ] M2.3 Trip generator with route segments and road types
- [ ] M2.4 Backfill mode into canonical samples; ground truth writer
- [ ] M2.5 `vehicle.dbc`; CAN feeder over `VGPT_CAN_INTERFACE`; UDP feeders (SOME/IP, VHAL, QNX, UDS mocks)
- [ ] M2.6 Scenarios: `clean_21d`, `range_decay`, `fast_charge_overtemp`, `adas_dropouts`, `city_vs_highway`, `demo_21d`
- [ ] M2.7 Tests: same seed gives identical ground truth; DBC round trip; physics sanity (energy balance, thermal bounds)
Gate: `demo_21d` backfill under 10 minutes; ground truth file reviewed by the human; plots of key signals attached.

## M3 Ingest and event detection v1
- [ ] M3.1 `SignalSource` adapters: CAN, SOME/IP-mock, VHAL-mock, QNX logs, UDS-mock
- [ ] M3.2 Canonicaliser; clock handling; drop, duplicate and out-of-order tolerance
- [ ] M3.3 `ReadOnlyBus`; safety tests S1 S2
- [ ] M3.4 Pipeline: batching to store, hot ring, derived signals (`energy_wh_per_km`, `road_type`, trips)
- [ ] M3.5 Detectors: limit, rate-of-rise, DTC and ADAS passthrough; event append with black-box scheduling
Gate: live 1x run ingests three sources with under 1% loss; `fast_charge_overtemp` yields exactly one event with a complete black-box window.

## M4 Insight engine
- [ ] M4.1 Baselines per vehicle state; robust z; contributor ranking
- [ ] M4.2 `EvidencePack` builder for events; template narration for all kinds
- [ ] M4.3 Drift scan (robust z, CUSUM) and efficiency change-point; trip summary insights
- [ ] M4.4 Delivery policy (severity, state, dedup, daily budget, dismissal suppression); insight queue and lifecycle
- [ ] M4.5 Case files for DTC events
- [ ] M4.6 Tests against ground truth; `clean_21d` false-alert gate
Gate: ground-truth comparison report passes; zero critical false alerts on `clean_21d`.

## M5 Ask engine
- [ ] M5.1 `LLMClient` Protocol; `FakeLLM`; `LlamaServerClient` with json_schema output
- [ ] M5.2 `QueryPlan` schema and resolver (time); router with rules and embeddings
- [ ] M5.3 Tools: trend, driver_decomposition, changepoint, events, pre_event_scan, compare_segments, trip_summary
- [ ] M5.4 Narrator, templates, verifier (property tests)
- [ ] M5.5 Ask orchestration with stage timings; follow-up context; unsupported handling
- [ ] M5.6 `bench/golden/questions.yaml` v1 (60 questions) and runner
Gate: golden set intent at least 95% and evidence at least 95% on `FakeLLM`; model suite results recorded for 0.5B and 1.5B.

## M6 API
- [ ] M6.1 FastAPI app, auth roles, error format, OpenAPI
- [ ] M6.2 REST routes; SSE `/ask`; WebSocket `/stream`
- [ ] M6.3 Metrics and health; store size; wipe route
- [ ] M6.4 Generate `apps/web/lib/api-types.ts` in CI with drift check
- [ ] M6.5 API tests including role checks and SSE ordering (`route, card, token*, verified, done`)
Gate: contract tests green; `curl` demo of an ask streaming.

## M7 UI
- [ ] M7.1 IVI: status row, zones A B C, modes, tokens, states
- [ ] M7.2 WebSocket live updates; insight enter animation; narration swap
- [ ] M7.3 Ask panel with SSE card, tokens, verified label, chips
- [ ] M7.4 Service UI: events table, event detail with uPlot timeline, case file, export, health panel
- [ ] M7.5 Playwright tests and screenshots of every state; accessibility pass
Gate: browser-agent recording of the demo script steps 2 to 5; no non-local requests.

## M8 Packaging and benchmarks
- [ ] M8.1 Dockerfiles (amd64 and arm64), Compose profiles `dev`, `a55`, `hpc`, resource caps, egress-less core network
- [ ] M8.2 `make demo` one command; seeded history loads automatically; reset script
- [ ] M8.3 `bench.run`: latency by stage, RSS, ingest loss, storage; results to `bench/results/`
- [ ] M8.4 Model comparison table (0.5B, 1.5B, Llama-3.2-1B)
- [ ] M8.5 README quick-start; demo script as `docs/DEMO.md`; architecture diagram export
Gate: all NFR gates in `PRD.md` measured and reported honestly; update the poster numbers from the report.

## M9 Stretch (only after M8)
- [ ] M9.1 CARLA bridge and OpenSCENARIO fault scripts
- [ ] M9.2 Cuttlefish VHAL adapter; vsomeip adapter; QNX forwarder stub
- [ ] M9.3 Local voice: whisper.cpp tiny and Piper
- [ ] M9.4 SQLCipher store; block-compressed warm tier
- [ ] M9.5 Rust ingest port behind `SignalSource`
- [ ] M9.6 LoRA-tuned planner; fleet and validation digest page
