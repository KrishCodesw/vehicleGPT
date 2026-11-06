# Invariants (always on)

These override convenience. If a task seems to require breaking one, stop and ask the human.

1. No transmit path from `vgpt/ingest`, `store`, `insight`, `ask`, `api` to any bus or actuator. Only `vgpt/sim` transmits. Use `ReadOnlyBus` everywhere else.
2. The core makes no outbound network call at runtime. No telemetry, no font or script CDNs in the web app, no package downloads at runtime.
3. The LLM outputs JSON plans or narration only. It never writes SQL, code or shell. Tools take bound parameters.
4. Every number or time in narrated text must be in the evidence facts. Never bypass or mock the verifier outside unit tests of the verifier itself.
5. Everything has a no-LLM path (templates, `FakeLLM`). Features must degrade, not fail, when the model is down.
6. Advisory copy only. Never tell a driver to take a safety action. Native warnings stay first-line.
7. Coarse location only (geohash 5). No raw video or audio stored. No PII or tokens in logs.
8. Time is epoch ms UTC from `vgpt.common.clock`. No `datetime.now()` or `time.time()` in product code.
9. UI numbers come from the API. Never hard-code vehicle values in components (fixtures only in tests and stories).
10. Do not weaken a test, gate or safety check to make something pass. Fix the cause or ask.
11. Do not use browser speech APIs; they call the cloud.
12. Keep the contracts in `docs/` truthful: change the doc in the same commit as the code.
