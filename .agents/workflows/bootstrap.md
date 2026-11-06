---
description: Set up the repo, tools and models from a clean clone (M0 checks)
---
1. Read `AGENTS.md`, `docs/TASKS.md` (M0) and `docs/DECISIONS.md`.
2. Check prerequisites: Python 3.12, uv, Node 20+, pnpm, Docker. Report any missing tool and stop; do not install system packages without asking.
3. Run `make setup`. This is the only step allowed to use the network (Python and npm packages, GGUF models into `models/`).
4. Run `make test lint safety`. Fix failures in code, not in checks.
5. Run `docker compose config` and confirm resource caps match `docs/ARCHITECTURE.md` section 2.
6. Print a short report: tool versions, model files present with sizes, test counts, anything skipped and why.
7. Update the Status Log in `docs/TASKS.md` only if the M0 gate fully passes.
