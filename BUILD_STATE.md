# Site Build State — semptify.org bill microsite

What's live, what's pending. Updated when state changes — not a changelog
(see OPERATIONS_LOG.md for that).

## Live now

- `semptify.org/bill` microsite — self-contained, Cloudflare Worker,
  ~5min cache. Pages: home, bill, live, research,
  what-the-bill-changes, your-voice.
- App-origin redirects: `semptify-jsam.onrender.com/bill*` → 301 to
  `semptify.org/bill*` (shipped PR #330, verified live).
- Dark mode, public anonymous APIs, voice-post lane — all verified
  2026-11-05 audit.

## Pending / known gaps

- **Retire the 5 app bill templates** (`your_voice.html`, `bill_draft.html`,
  etc. under `app/templates/`) — unreachable since the 301s, but still in
  the repo. Blocked on another session's copy pass landing first.
- **Voice post test residue** — one unpublished test post may remain in
  the review queue; delete when convenient.
- **Neon/DB**: pool retune shipped (#332) — compute now suspends after
  ~5 idle min. Watch first-week CU-hours vs the ~20/mo burn.

## Last verified

- 2026-11-05 — redirects 301 on origin, microsite serving, dark mode OK,
  anonymous GETs 200, POST-only routes 405 correctly.
