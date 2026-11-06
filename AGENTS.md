# VehicleGPT Edge: agent instructions

## Mission
Build VehicleGPT Edge end to end: an on-device, cloud-free vehicle assistant that (1) proactively explains vehicle events, slow drifts and trips, and (2) answers natural-language questions over weeks of vehicle history. Target: ~2 GB RAM, 2 ARM A5x-class cores, answer card < 1 s, zero write path to the vehicle. Context: Tata Elxsi Teliport S4, Case Study 5. Write demo-quality software with a production-shaped architecture.

## Read first, in this order
1. `docs/PRD.md` (what and why, requirement IDs FR-*/NFR-*)
2. `docs/ARCHITECTURE.md` (components, contracts, budgets)
3. `docs/TASKS.md` (find the current milestone; work only on it)
4. The doc for the area you touch: `DATA_MODEL`, `AI_PIPELINE`, `SIMULATION`, `API_SPEC`, `UX_SPEC`, `SAFETY_SECURITY`, `TEST_PLAN`
5. `docs/DECISIONS.md` lists settled choices. Do not reopen them; ask the human first.

## Repo map
- `vgpt/common` config, clock, ids, units, pydantic schema
- `vgpt/sim` vehicle model, scenarios, DBC, feeders, backfill, ground truth
- `vgpt/ingest` adapters (CAN, SOME/IP-mock, VHAL-mock, QNX logs, UDS), canonicalisation, read-only guard
- `vgpt/store` hot ring, SQLite warm/cold, black-box windows, FTS, retention
- `vgpt/insight` detectors, evidence packs, contributors, drift, trips, delivery policy, case files
- `vgpt/ask` router, planner, query-plan schema, tools, narrator, verifier, LLM clients
- `vgpt/api` FastAPI REST + SSE + WebSocket
- `vgpt/core` wiring (`python -m vgpt.core`)
- `apps/web` Next.js: IVI screen (`/ivi`) and service UI (`/service`)
- `bench/` golden questions and benchmark harness; `tests/`; `deploy/`; `scripts/`
- `data/` and `models/` are gitignored runtime folders

## Commands (create the Makefile in M0)
- `make setup` uv sync + pnpm install + fetch models (the only step that may use the network)
- `make test` pytest + web unit tests; `make lint` ruff + mypy + eslint + tsc
- `make demo` start sim + core + llm + web with the `demo_21d` history loaded
- `make bench` golden questions, latency and memory harness
- `make safety` static and runtime safety checks (see `docs/SAFETY_SECURITY.md`)

## Non-negotiable invariants
1. No write path to any vehicle bus or actuator from `vgpt/ingest`, `store`, `insight`, `ask`, `api`. Only `vgpt/sim` may transmit.
2. The core process makes no outbound network calls at runtime. Loopback and the compose network only.
3. The LLM never writes SQL or code. It emits a JSON query plan, validated by pydantic, executed by parameterised tools.
4. Every number in a narrated answer must be in the evidence facts. The verifier blocks the rest and falls back to a template.
5. Everything works without an LLM (template narration, `FakeLLM` in tests). The model improves wording; it is never required for correctness.
6. Copy is advisory: say "contributing factors in the data", never instruct safety-critical actions, native warnings stay first-line.
7. Privacy: coarse location only (geohash precision 5), no raw video stored, no PII in logs.
8. Timestamps are epoch milliseconds UTC. Use `vgpt.common.clock`, never `datetime.now()` directly.

## Conventions
- Python 3.12, uv, ruff, mypy strict on `vgpt/`, pydantic v2, asyncio. Type everything. No global mutable state.
- Interfaces are `typing.Protocol` in each package's `base.py`. Implementations are swappable by config.
- Small modules, one responsibility. Public functions have docstrings stating units and time bases.
- Tests first for detectors, tools, verifier, store. Property tests (hypothesis) for the verifier and unit conversions.
- Web: TypeScript strict, Next.js app router, Tailwind with the tokens in `docs/UX_SPEC.md`, uPlot for charts. No Inter, no emoji, no gradient text.
- Commits: small, imperative, one concern. Reference the task ID (e.g. `M3.2: add overtemp detector`).

## How to work (Antigravity)
- For any task larger than ~100 lines, first produce an Implementation Plan artifact: files to touch, interfaces, test list, risks. Wait for approval on milestone starts.
- Implement in the smallest vertical slice that passes its acceptance test, then widen.
- After each task run `make test lint safety`. Do not mark a task done in `docs/TASKS.md` until they pass.
- For UI work use the browser agent: screenshot each state listed in `docs/UX_SPEC.md` and attach the recordings.
- Append a dated line to the Status Log in `docs/TASKS.md` when a milestone gate passes.
- Use the workflows `/bootstrap`, `/run-scenario`, `/verify-milestone`, `/benchmark` and the skills `add-detector`, `add-ask-tool`.

## Definition of done
Acceptance criteria in `docs/TASKS.md` pass; tests added; lint and types clean; invariants untouched; docs updated if a contract changed (`API_SPEC`, `DATA_MODEL`, `AI_PIPELINE`); no TODOs left without a task ID.

## Ask the human before
Adding a dependency outside the approved stack; changing a contract in `docs/*`; changing a decision in `DECISIONS.md`; anything that touches network egress, auth or the read-only guard; deleting data folders; running commands that need sudo.

## Never
Disable or weaken a safety check to make a test pass; mock away the verifier; use browser speech APIs (they call the cloud); commit model files or `data/`; invent vehicle numbers in UI copy that are not computed from the store.
