# Bill Mirror — Agent Guide

The public face of the Minnesota Rent Assurance Bill — a self-contained
static microsite, deliberately independent of the Semptify app.
`README.md` is the canonical layout/build reference; `BUILD_GUIDE.md`,
`BUILD_STATE.md`, and `OPERATIONS_LOG.md` carry ship state.

## Build contract

- Edit `src/pages/*.html`, `src/partials/*`, `src/bill.css` — never the
  root `*.html` directly. Root files are build output AND the served
  contract: run `python build.py`, then commit the root files with the
  source changes (the Cloudflare Worker pulls root files from GitHub,
  ~5 min cache).
- `build.py` runs `sync_assets.py --check` first — every vendored app
  asset must match its source or the build fails.
- `worker.js` (repo root) `PAGES`/`ASSETS` maps are the URL contract —
  a new page or `/static/*` asset needs a map entry AND a worker
  redeploy or it 404s in prod. Root filenames are fixed; do not rename
  pages.

## Design rules that hold (full list in README §"Design rules")

- Zero external stylesheet deps — `bill.css` only, inlined per page.
- Light-only pinned northstar palette — no `prefers-color-scheme` flips.
- One nav, one link set — `nav.html` and `nav_deck.html` mirror each
  other; update both.
- The Semptify seam is data-only (`/api/*` proxy); layouts never cross.
- This repo IS the public surface — Semptify public-side rules apply to
  every page: no advertising, no promoting third-party services, no
  business-model language, no user PII.

## The Happiness Factor — simplicity-first, the 5-step algorithm (Brad, 2026-11-11)

Run on every page, section, and change, in order:

1. **Goal** — state it in one sentence. Can't? Stop.
2. **Minimum set** — the smallest set of parts that reaches the goal.
3. **Justify the rest** — every part beyond the minimum must justify
   itself against the goal.
4. **Subtract-first review** — look for what to remove before what to
   add.
5. **Fewer parts win ties** — equal options → take the one with fewer
   parts.

This is a public site for readers in a hurry. Every section, nav item,
and line of copy is a "part." Canonical twin:
`modules/app-semptify-fastapi/.devin/rules/11-simplicity-first.md`.
