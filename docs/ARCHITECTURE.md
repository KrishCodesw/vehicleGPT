# Architecture

## 1. Shape
```
 VEHICLE SIDE (simulated)                 |  EDGE AI DOMAIN (QM, containerised)                 |  USERS
 vgpt/sim: vehicle model, scenarios       |                                                     |
  CAN/CAN-FD (python-can)  ------------>  |  ingest ---> canonical samples ---> store           |  IVI (Next.js /ivi)
  SOME/IP-mock (UDP JSON)  ------------>  |   (read-only guard)       |   hot ring (RAM)        |  Service UI (/service)
  VHAL-mock    (UDP JSON)  ------------>  |                           |   warm (SQLite, 14 d)   |
  QNX logs     (UDP syslog)------------>  |   one-way diode           |   cold (rollups, 90 d)  |
  UDS/DoIP-mock(UDP JSON)  ------------>  |   = no TX code in core    |   black-box, FTS5       |
                                          |                           v                         |
                                          |  insight engine <--- tools (parameterised) ---> ask engine
                                          |   detectors, evidence, policy     router, planner, narrator, verifier
                                          |                    \                 /
                                          |                     api (FastAPI: REST, SSE, WS)  --+--> web
                                          |  llama-server (separate process, GGUF Q4_K_M)       |
```
The diode is a property of code and deployment: the core has no transmit path, the container has no outbound network, and tests enforce both.

## 2. Processes (Compose services)
| Service | Role | Budget (a55 profile) |
|---|---|---|
| `sim` | Vehicle side. Only component allowed to transmit. | outside the 2 GB budget |
| `core` | ingest + store + insight + ask + api in one asyncio process | RSS 450 MB |
| `llm` | llama-server, 0.5B Q4_K_M, ctx 2048, mmap | RSS 600 MB |
| `web` | Next.js HMI stand-in | outside the budget |
Total in-vehicle budget about 1.2 GB including OS, leaving headroom under 2 GB.

## 3. Package responsibilities and interfaces (`base.py` Protocols)
- `ingest.base.SignalSource`: `async def frames() -> AsyncIterator[RawFrame]`; adapters: `CanSource`, `SomeIpMockSource`, `VhalMockSource`, `QnxLogSource`, `UdsMockSource`.
- `ingest.canonical`: raw frame to `Sample(vehicle_id, ts_ms, signal, value, quality)` or `LogLine` or `DtcRecord`.
- `store.base.Store`: `write_samples`, `read_series`, `read_rollup`, `snapshot_blackbox`, `append_event`, `query_events`, `search_text`, `size_report`, `purge`. Impl: `SqliteStore`; hot ring `HotBuffer` (numpy).
- `insight.base.Detector`: `on_sample(batch) -> list[EventCandidate]`; `ScanDetector.scan(store, now) -> list[EventCandidate]` for nightly drift.
- `insight.evidence.build(event, store) -> EvidencePack`; `insight.policy.decide(insight, vehicle_state, history) -> Delivery`.
- `ask.base.AskTool`: `name`, `args_model`, `run(args, store, clock) -> ToolResult(facts, table, chart, refs)`.
- `ask.llm.base.LLMClient`: `complete_json(prompt, schema)`, `stream_text(prompt)`; impls `LlamaServerClient`, `FakeLLM`.
- `api`: thin; no logic beyond auth, validation and streaming.

## 4. Key flows
Event flow (proactive)
1. Samples arrive, canonicalised, written to hot ring and warm store (deadband).
2. Detector emits `EventCandidate`. Store appends `event`; a black-box snapshot is scheduled for event time plus 60 s.
3. `evidence.build` computes window stats, baseline comparison, ranked contributors, facts.
4. Template narration is attached immediately; `policy.decide` queues delivery; WS pushes `insight.created`.
5. Background task asks the model to narrate the evidence pack; verifier checks; on pass the insight text is upgraded and cached.

Ask flow (reactive)
1. `POST /v1/ask` with text and optional `insight_id`.
2. Router returns intent (fast path) or asks the planner for a JSON plan.
3. Tools run on the store; result becomes an evidence pack. Emit SSE `card` (numbers, chart spec).
4. Narrator streams tokens (SSE `token`); verifier runs on the full text; emit `verified` true or the template replaces it; emit `done`.

## 5. Concurrency and resource rules
- One asyncio loop. CPU-heavy tools run in a small `ProcessPoolExecutor` (max 1 worker on `a55`).
- SQLite: WAL, `synchronous=NORMAL`, one writer task, read connections per request, `busy_timeout` 2000 ms, `mmap_size` 64 MB, `cache_size` 16 MB.
- Ingest batches writes every 1 s. Hot ring: fixed arrays per signal, 15 min at native rate.
- Backpressure: if the writer lags more than 5 s, drop oldest hot samples and increment `dropped_samples`.
- Model: one request at a time per llama slot; the proactive narrator yields to interactive asks (priority queue).
- Memory guard: if RSS exceeds 90% of budget, disable model narration and use templates until it recovers.

## 6. Profiles
| Profile | Model | Threads | Notes |
|---|---|---|---|
| `dev` | Qwen2.5-1.5B Q4_K_M | 4 | laptop |
| `a55` | Qwen2.5-0.5B Q4_K_M | 2 | benchmarked in a container capped at 2 CPUs and 2 GB |
| `hpc` | 3B+ | 6+ | richer narration, longer context; same API |
Profiles only change config (model path, threads, context, budgets), never code paths.

## 7. Configuration
Environment variables with a pydantic `Settings` class: `VGPT_PROFILE`, `VGPT_DATA_DIR`, `VGPT_CAN_INTERFACE` (`socketcan|udp_multicast|virtual`), `VGPT_LLM_URL`, `VGPT_SIM_SEED`, `VGPT_CLOCK` (`wall|sim`), `VGPT_TOKENS` (role tokens, dev only).

## 8. Observability
Structured JSON logs without PII. Metrics (in-process, exposed at `/v1/metrics` and in a UI panel): RSS, p50/p95 ask latency by stage (route, plan, tools, card, ttft), ingest rate, dropped samples, queue depth, verifier block rate, model fallback rate.

## 9. Failure modes
| Failure | Behaviour |
|---|---|
| llama-server down or slow | Templates and fast-path cards continue; UI shows "model offline". |
| Store locked | Retry with backoff; ingest buffers in the hot ring. |
| Unknown signal in frame | Count and log once; ignore. |
| Planner returns invalid JSON | One constrained retry; then intent `unsupported` with a helpful message. |
| Verifier fails twice | Template narration; `verified=false`. |
