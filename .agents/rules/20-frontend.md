# Frontend rules (apply to `apps/web/**`)

- Next.js app router, TypeScript strict, Tailwind with the tokens in `docs/UX_SPEC.md`. Charts with uPlot. State: React state and a small store; no heavy state libraries.
- Fonts: Barlow and Barlow Semi Condensed, self-hosted. No Inter, Space Grotesk, Roboto or Poppins. No Google Fonts link at runtime.
- No emoji, no gradient text, no decorative glow, no icon-in-card grids, no purple or indigo gradients. One accent (`#FF4A1C`) for one active item at a time. Plain, quiet, readable.
- IVI minimum text size 16 px; touch targets at least 48 px; contrast at least 4.5:1; tabular numerals for numbers.
- Every state in `UX_SPEC.md` section 4 must exist: loading, empty, error, model offline, template answer, held insight, reconnecting.
- Motion: transform and opacity only; 150 to 200 ms; ease-out `cubic-bezier(0.23, 1, 0.32, 1)`; buttons scale to 0.97 on `:active`; hover styles only inside `@media (hover: hover) and (pointer: fine)`; honour `prefers-reduced-motion`; never animate values that tick often; never animate from `scale(0)`.
- Accessibility: semantic elements, real buttons, visible focus ring, `aria-live="polite"` for new insights, text alternative for each chart.
- Network: only the local API origin. Generated types in `lib/api-types.ts` are never edited by hand.
- Testing: Playwright for each state and the demo script; vitest for pure logic. Use the browser agent to capture screenshots and check the network log.
- Copy: plain words, units on all numbers, at most three sentences per answer, never an instruction to take a safety action.
