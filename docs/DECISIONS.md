# Decisions (settled; ask before changing)

| ID | Decision | Why |
|---|---|---|
| D1 | Python 3.12 backend for the MVP. Optional Rust port of ingest in M9 behind the same interfaces. | Fastest path to a working end-to-end demo. |
| D2 | One asyncio core process (ingest, store, insight, ask, api). `llama-server` runs as a second process. | Saves RAM; two processes fit the 2 GB budget. |
| D3 | SQLite (WAL) only for vehicle data. No Postgres, Redis, Kafka or vector DB in the vehicle path. | Footprint, offline, simplicity. |
| D4 | LLM emits a JSON query plan; parameterised tools run it. The model never writes SQL. | Accuracy, safety, prompt-injection resistance. |
| D5 | Inference through `llama-server` (llama.cpp), GGUF Q4_K_M. Defaults: Qwen2.5-1.5B-Instruct (dev), Qwen2.5-0.5B-Instruct (a55). Alternate: Llama-3.2-1B-Instruct. | Runs on ARM CPUs, grammar-constrained JSON, permissive licences for 0.5B/1.5B. |
| D6 | Lightweight physics-based simulator first; CARLA is an optional adapter (M9). | CARLA needs a GPU and slows iteration. |
| D7 | CAN transport via python-can: `socketcan` (Linux vcan), `udp_multicast` (portable, default off Linux), `virtual` (tests). | Works on any dev machine. |
| D8 | Next.js web app stands in for the vehicle HMI. No Android Automotive app. | Scope. |
| D9 | Narration is verified; template fallback always exists; tests use `FakeLLM`. | Determinism and trust. |
| D10 | Advisory-only copy; native vehicle warnings remain first-line. | Safety positioning. |
| D11 | No browser speech APIs. Voice is local whisper.cpp + Piper only, and only in M9. | Chrome speech calls the cloud. |
| D12 | Time is epoch ms UTC; the simulator owns a simulated clock; `vgpt.common.clock` is the only time source. | Reproducible backfill and tests. |
| D13 | uv for Python, pnpm for web, Docker Compose for the demo, ruff + mypy + pytest. | Speed and reproducibility. |
| D14 | Single vehicle in the MVP; `vehicle_id` column reserved in every table. | Fleet later without migration pain. |
| D15 | Plain SQLite in the MVP; SQLCipher behind the `Store` factory in M9. | Avoids build pain early. |
| D16 | Warm tier uses deadband + heartbeat writes, not raw 1 Hz rows. | Cuts storage roughly 10x on slow signals. |
