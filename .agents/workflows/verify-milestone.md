---
description: Check a milestone against its gate before moving on
---
Input: milestone ID (for example M3).
1. Open `docs/TASKS.md`; list the milestone's tasks and gate.
2. Run `make test lint safety`. Any failure stops the workflow; fix first.
3. Run the gate command or demo described in the milestone. For UI milestones use the browser agent and capture a recording and a screenshot of every state in `docs/UX_SPEC.md` section 4.
4. Check invariants: grep for `.send(` outside `vgpt/sim`; confirm no new outbound network usage; confirm contract docs match the code (`API_SPEC`, `DATA_MODEL`, `AI_PIPELINE`).
5. Write a gate report as an artifact: tasks done, test counts, metrics against the targets in `docs/PRD.md` section 8, deviations, open risks.
6. If everything passes, tick the milestone's boxes, add a Status Log line, and ask the human for approval to start the next milestone. Do not start it on your own.
