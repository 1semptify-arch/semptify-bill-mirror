# Site Build State — semptify.org bill microsite

What's live, what's pending. Updated when state changes — not a changelog
(see OPERATIONS_LOG.md for that).

## Live now (verified 2026-11-10)

- `semptify.org/bill` microsite — self-contained, Cloudflare Worker
  (`bill-mirror`), ~5min page cache. **All 11 routes live:** home, bill,
  live, research, what-the-bill-changes, your-voice, history, providers,
  brief, classroom, press, myths.
- Worker URL map complete: 6 `/bill/*` routes + `brain.js` added
  2026-11-10 (worker.js now versioned in this repo — see README).
- Previously-404 assets fixed same pass: `doc-page.jpeg` (paper texture —
  was broken on every interior page), `loon.png`, `mn-flag.png`,
  `semptify-live-001-cover.jpg`.
- `brain.js` live — tools-rail anchors, rail board widget, live badge,
  30s polling all active in prod.
- Board pipeline verified end-to-end: POST `/api/voice-post` → Neon →
  `awaiting_review` increments; GET `/api/voice-posts` public.
  Moderation lane: `/admin/public-voice` (app admin).
- App-origin redirects: `semptify-jsam.onrender.com/bill*` → 301 to
  `semptify.org/bill*` (verified 2026-11-10).
- Dark mode, anonymous APIs — verified 2026-11-05 audit; markup confirmed
  unchanged since.

## Pending / known gaps

- **Voice review queue** — 4 posts awaiting moderation at
  `/admin/public-voice`, including one `probe-do-not-post` test row
  (decline it). Public board shows "Nothing posted yet" until first
  publish — decide whether to seed.
- **Retire the 5 app bill templates** (`your_voice.html`,
  `bill_draft.html`, etc. under `app/templates/`) — unreachable since the
  301s, but still in the repo. Blocked on another session's copy pass.
- **Retire legacy `home.html`** — still served at `/`; decision logged.
- **`cherry.jpg`** — 31KB unreferenced asset at root; delete or keep.
- **Neon/DB**: pool retune shipped (#332) — compute suspends after
  ~5 idle min. Watch first-week CU-hours vs the ~20/mo burn.
- **Parallel-session commits** — ssot sync + ops-log commits from a
  concurrent agent session were unpushed at time of worker deploy;
  pushed together with this state update.

## Last verified

- 2026-11-10 — all 11 routes 200, brain.js + previously-404 images 200,
  content-types correct, AI binding preserved, POST→DB write path proven
  (awaiting_review 3→4 on probe).
