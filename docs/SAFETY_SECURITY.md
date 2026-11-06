# Safety, security, privacy

Scope: demonstrate isolation by construction and by test. This is not a certification claim. Standards are alignment targets (ISO 26262 freedom from interference, ISO/SAE 21434, UN R155) for the production path.

## 1. Isolation invariants
| ID | Invariant | Enforcement |
|---|---|---|
| S1 | No transmit path from the AI side to any bus or actuator | `ReadOnlyBus` wrapper raises on `send`; CI grep fails on `.send(`, `send_periodic`, `Message(` construction outside `vgpt/sim`; runtime test tries to write and expects `ReadOnlyViolation` |
| S2 | Core makes zero outbound network calls | Compose `core` on an internal network with no egress; test starts core with egress blocked and asserts no connection attempts (socket audit hook in test mode) |
| S3 | Model output cannot execute anything | Output is JSON validated by pydantic; tools take bound parameters; no `eval`, `exec`, `subprocess` in `vgpt/ask` (CI grep) |
| S4 | Advisory copy only | Narrator prompt and templates reviewed; lint test scans templates for imperative safety verbs ("stop", "pull over", "disable", "ignore") |
| S5 | AI failure never degrades vehicle functions | Core is a separate container with CPU and memory caps; chaos test kills `llm` and `core`; sim vehicle state is unaffected by construction |
| S6 | Native warnings stay first-line | UI never suppresses or restyles a native warning; AI banners are secondary |

## 2. Threat model (informational)
| Threat | Example | Mitigation | Test |
|---|---|---|---|
| Prompt injection via logs | QNX log line says "ignore previous instructions" | logs never reach the planner; narrator gets log text only inside `<data>` fences, truncated, marked untrusted; verifier checks numbers anyway | injected-log test |
| Malicious query | "Disable the battery warning" | `unsupported` plus read-only statement | refusal test |
| SQL injection | planner returns signal `x; DROP TABLE` | closed catalogue validation; bound parameters | fuzz test |
| Data exfiltration | model asked to send data out | no egress; no network tools | S2 |
| Unauthorised access | driver token calls `/cases` | role checks; 403 | API tests |
| Tampering at rest | edited DB | M9: SQLCipher, key in TPM; integrity checks on event rows | later |
| Resource exhaustion | flood of frames or queries | rate limits, hot ring bounds, request timeouts, memory guard disables model narration | load test |

## 3. Privacy
Local-only processing. Location stored as geohash precision 5 only. No raw camera frames or audio stored; camera data is detections and a confidence number. Logs contain no tokens, no free-text user questions beyond a hash and length (store full questions only if `VGPT_DEBUG_QUESTIONS=1`). Driver-visible data wipe: `POST /v1/store/wipe` (service role) deletes insights, events, history; requires confirmation phrase. Retention per `DATA_MODEL.md`.

## 4. Auth
Dev: static role tokens. Production path: mTLS for the service UI and a local pairing flow for the IVI. Tokens never logged. CORS restricted to the local origin.

## 5. `make safety`
Runs: static greps (S1, S3, S4), read-only violation test, egress test, API role tests, injection tests, SQL fuzz tests. Must pass on every commit.
