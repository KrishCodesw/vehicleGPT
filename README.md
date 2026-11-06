# VehicleGPT Edge: agent pack

This folder is the starting kit for building VehicleGPT Edge with Google Antigravity (or any agent that reads `AGENTS.md`).

## Use it
1. Create the repo `vehiclegpt-edge`, copy this pack into the root, and open the folder in Antigravity.
2. Rules: `AGENTS.md` is read automatically. Do not add a `GEMINI.md`; Antigravity gives it precedence over `AGENTS.md` and the two would drift. In Antigravity's Customizations panel set `.agents/rules/00-invariants.md` to Always On, `10-backend-python.md` to a glob on `vgpt/**/*.py`, and `20-frontend.md` to a glob on `apps/web/**`.
3. Folder note: new installs read `.agents/` (rules, workflows, skills). Older builds read `.agent/`. If yours does, rename the folder. Check https://antigravity.google/docs/rules-workflows for the current path.
4. Each rule, workflow and `AGENTS.md` must stay under 12,000 characters (Antigravity limit). They all do.
5. Start with this prompt: "Read AGENTS.md, then docs/PRD.md, docs/ARCHITECTURE.md and docs/TASKS.md. Produce an Implementation Plan for milestone M0 only. Do not write code until I approve."
6. Then work one milestone at a time. Use `/verify-milestone` before moving on.

## What is in the pack
- `docs/PRD.md` product requirements, scope, demo script, traceability to the brief
- `docs/ARCHITECTURE.md` components, contracts, resource budgets, profiles
- `docs/DATA_MODEL.md` signal catalogue, SQL schema, retention, write policy
- `docs/AI_PIPELINE.md` router, query-plan schema, tools, evidence packs, narrator, verifier
- `docs/SIMULATION.md` vehicle model, scenarios, adapters, ground truth
- `docs/API_SPEC.md` REST, SSE and WebSocket contracts
- `docs/UX_SPEC.md` IVI and service UI, tokens, states, copy rules
- `docs/SAFETY_SECURITY.md` isolation, threat model, privacy
- `docs/TEST_PLAN.md` golden questions, benchmarks, gates
- `docs/TASKS.md` milestones M0 to M9 with acceptance criteria and a status log
- `docs/DECISIONS.md` settled technical choices
- `.agents/` rules, workflows, skills

## Two cautions
- The competition terms say a submitted idea becomes Tata Elxsi's property. Read the Round 2 terms before you open-source anything.
- Numbers on the poster are design targets. Milestone M8 produces the measurements; update the poster from those.
