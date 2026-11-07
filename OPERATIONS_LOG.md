# Site Operations Log — semptify.org

Dated record of site-affecting operations. Newest first. Format:
`YYYY-MM-DD — what changed — where verified`.

## 2026-11-07

- **Static-asset sync automated** (swe-2): new `sync_assets.py` syncs all
  app-sourced copies (root css/js/img + the vendored ssot sections inside
  `src/bill.css`) from `../modules/app-semptify-fastapi`, with `--check`
  mode reporting drift. `build.py` runs the check before every build —
  stale assets now fail loudly instead of shipping silently (root cause
  of the northstar dark-pin / ssot fill-fix drift). Synced `ssot.css`
  (was missing the dark-mode paper-text-on-primary-fill rules).
- **Six new bill-wing spaces built** (swe-2, architecture draft §5):
  history (public version history — build.py now merges `git log` from
  this repo + the app repo's bill canon into a dated table with GitHub
  commit links), providers, lawmakers' brief, classroom kit, press room,
  myths & facts. New links added to rail_top, nav_deck, rail_tools, and
  cover panels. preview_server.py aliases added for the six routes;
  port 8791 registered in PORTS.md. Verified via build + local preview.
  NOT pushed — deploy needs the six `/bill/*` routes added to the
  Cloudflare Worker URL map first (dashboard-only source).

## 2026-11-05

- **DB pool retune shipped** — `NullPool` on `render_balanced` (#332) +
  SSOT redirect fix (#333), deploy `dep-dbmadglbedkc73bmlb6g`.
  Verified: Neon compute `ep-cold-surf` went idle/suspended 16:05Z after
  ~5.5 min quiet — first time it ever could. CU-hour burn closed.
- **Bill 301s verified on origin** — all five `/bill*` paths redirect to
  semptify.org (PR #330, carried in same deploy).
- **Decision engine live** — desk at 127.0.0.1:8600/desk; orchestrator +
  review pages retired to redirects (consolidation pass).

## 2026-11-04 → 2026-11-05 (earlier)

- Public-site audit fixes — dark-mode collisions on /bill/research,
  non-200 assets, live-draft sanitization (strikethrough, no filenames,
  no user name), anonymous API behavior (PR #326).
- Dead CSS System 3 removed — PR #329 merged.
- Module-registry workflow fixed to PR-flow — PR #328 merged.
- `render_balanced` profile deployed — embeddings + registry kept,
  Positronic Brain/Mesh/monitoring off.

## Standing notes

- Cloudflare worker cache ~5 min — "pushed but not live" is usually cache.
- App origin bill paths MUST stay 301 — a 200 there means the stale twin
  is back.
- Neon free plan: suspend is fixed 5 min, not configurable — app-side
  connection behavior is the only lever.

## 2026-11-06

- **Desk scene replaces lake on interior pages** (swe-2, Brad's spec):
  sitter's-POV oak desk — worn front edge, haphazard written-on parchment
  stack left, fresh sheet front-center, ink bottle, quill resting right,
  half-burnt candlestick back-left. Animations: candle-flame flicker +
  halo/light pulse, quill lifts and writes left→right laying a visible
  ink line that fades, dust motes. Quill write disabled ≤700px (would
  smudge behind the content column); all motion off under
  prefers-reduced-motion. Lamplit parchment pool added behind .shell-main
  for heading contrast. Cover (/bill deck) keeps the lake scene.
  Built via build.py; verified locally at 1280px + 375px, console clean.
  NOT yet pushed — awaiting Brad's visual check.
- **Parchment liquid layout replaces desk scene** (swe-2, Brad's spec):
  flat warm parchment backdrop; true-liquid frame = low-profile Semptify
  bar (header) + bill nav top rail + tools rail left + options/board rail
  right + main + footer. brain.js (root) = logic layer: auto 'On this
  page' tool anchors, board polling /api/voice-posts every 30s into rail
  + full list on /your-voice, live badge, rail status text. Board =
  existing anonymous voice-posts API (bulletin board, not chat).
  Desk scene retired to git history (9353a37). preview_server.py now
  proxies /api/* to semptify.org. Verified: grid geometry + computed
  styles at 1280px via IronBee, structure snapshot clean. NOT pushed —
  awaiting Brad's visual check.
- **MN manuscript theme applied** — lake-dawn scene (mn-lake-sunrise.jpg)
  + MN flag + loon + cherry branch + ink-bottle/quill SVG on all bill
  pages; interior pages' cards now parchment (doc-page.jpeg texture);
  UnifrakturMaguntia blackletter + Pinyon Script calligraphy added to
  head.html. New assets at repo root: mn-flag.png, loon.png, cherry.jpg,
  doc-page.jpeg. Built via build.py; verified locally — all assets 200,
  fonts load. NOT yet pushed — awaiting Brad's visual check.
