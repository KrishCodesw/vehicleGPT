# UX spec

Two surfaces in one Next.js app: `/ivi` (in-car screen, dark glass) and `/service` (workshop UI, light). Match the poster: calm, legible, few words.

## 1. Tokens
| Token | IVI (dark glass) | Service (light) |
|---|---|---|
| ground | `#0B0D11` | `#E8EAED` |
| panel | `#151A21`, selected `#252B35` | `#DBDEE3` |
| ink | `#F5F7FA` | `#0D1014` |
| secondary | `#C2CAD4` | `#2F363F` |
| accent | `#FF4A1C` (one subject at a time: the hot or critical item) | same, sparingly |
| bar neutral | `#8E97A3` on track `#2A303A` | `#5C6571` on `#C3C8CF` |
Fonts: Barlow (body) and Barlow Semi Condensed (headings, large numbers), loaded locally in production (no CDN at runtime: self-host the woff2 files in `public/fonts`). Tabular numerals for all numbers.
Sizes (IVI): minimum 16 px; labels 16 to 17; body 18; values 32; headline 30 to 31. Touch targets at least 48 px. Contrast at least 4.5:1.
Radius: panels 16 to 20, pills fully round, buttons fully round. No gradient text, no emoji, no glow except the accent dot and bar on the one active item. No decorative icons.

## 2. IVI layout (1280x720 target, scales)
Status row: time, mode pill (Parked, Driving, Charging), ambient and range.
Three zones: A "Since you parked" feed (about 28%), B explanation panel (about 38%), C ask panel (about 34%).
- A: up to 3 insight items: short label, large value ("+11 °C", "-4%", "-0.2 bar"). Selected item has the accent dot.
- B: headline (plain sentence, at most 12 words), "Why" with up to 3 ranked contributors as labelled bars, one evidence line ("Evidence: 14:24 to 14:32"), buttons Show timeline and Explain more.
- C: conversation (user bubble, answer bubble), suggestion chips (max 3), input bar with mic (disabled until M9) and text field.
Driving mode: only a single banner for critical or warning events (one line, at most 12 words, plus "Details when parked"); zones A to C collapse to the status row and the banner; no text input.
Charging mode: same as parked, plus charge power and time to target.

## 3. Service UI
`/service`: events table (time, type, severity, subject, narration source), filters, search (FTS). `/service/events/[id]`: headline, ranked contributors, timeline chart (uPlot, 3 to 5 signals, event marker), DTC text, case file with "Export bundle". `/service/health`: metrics panel (RSS, latency by stage, ingest, dropped samples, verifier block rate, store size). Role login with a token field in dev.

## 4. States (all required; screenshot each with the browser agent)
Loading (skeleton at final dimensions, no spinner longer than 400 ms before a skeleton), empty ("Nothing to report since you parked."), error with retry, model offline (banner "Explanations are simplified right now"), verified=false (small label "Template answer"), stale data, held insight (policy hold), narration upgraded (text swaps with a 150 ms fade, no layout shift), connection lost (reconnecting pill).

## 5. Copy rules
Plain words, no jargon or signal names in headlines. Numbers always with units. Say "contributing factors in the data". Never instruct the driver to take a safety action; refer to the vehicle's own warnings. One idea per sentence. Maximum three sentences per answer. Show time as local 24 h `HH:MM`.

## 6. Motion (apply the motion and polish rules in the repo's rules)
Only transform and opacity. 150 to 200 ms, ease-out `cubic-bezier(0.23, 1, 0.32, 1)`. Buttons scale to 0.97 on press. Hover effects only under `(hover: hover) and (pointer: fine)`. No animation on high-frequency updates (values ticking). Respect `prefers-reduced-motion` (opacity only). New insight enters with a 180 ms fade and 8 px rise; never from scale 0.

## 7. Accessibility
Real buttons and inputs, visible focus ring (2 px, offset 2), labels on icon buttons, live region for new insights (`aria-live="polite"`), chart has a text summary, keyboard path through all zones.

## 8. Acceptance
Every state in section 4 exists and has a screenshot. Lighthouse accessibility at least 95. No request leaves the local origin (verify in the browser agent's network log).
