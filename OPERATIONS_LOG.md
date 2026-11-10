# Site Operations Log — semptify.org

Dated record of site-affecting operations. Newest first. Format:
`YYYY-MM-DD — what changed — where verified`.

## 2026-11-10

- **ssot.css sync + history regen** (swe-2, task
  plan-20261110-bill-mirror-run-sync-assets-py-ssot-css--efd9):
  drift check flagged root `ssot.css` stale vs app
  `static/css/ssot-design-system.css` — upstream added the
  `body.shell--dc-alt` A/B Document-Center layout block (flipped
  rail geometry). `sync_assets.py` synced the verbatim copy;
  vendored `src/bill.css` sections and all other tracked assets
  were already in lockstep. `build.py` regenerated all 11 root
  pages; only real diff = `history.html` picking up 3 new rows
  (canon 037fc2f9 + 73fb7648, site e79f555). Verified: preview on
  :8791 — `/bill/history` 200 with new rows rendered,
  `/ssot.css` 200 serving `shell--dc-alt`, IronBee console clean;
  py_compile PASS on build.py / sync_assets.py / preview_server.py;
  pytest test_ssot_architecture.py 7/8 — the one FAIL is
  pre-existing and unrelated (executive_admin/router.py:401 raw
  RedirectResponse; app-repo issue, logged as intake-eb3daf41,
  not touched). Committed 06d5b95. NOT pushed — `git push` is
  denied for headless runs.

- **Worker URL-map gap verified in prod — 6 routes serving wrong
  content** (swe-2, task
  plan-20261110-add-6-bill-routes-static-js-brain-js-to--e6ea):
  live probe of all 13 contract paths. The 5 original routes +
  `/static/js/law-linker.js` are worker-served and correct
  (`/bill` body = GitHub master `bill.html` + CF beacon injection
  — worker pulls current master, files need no push). The six new
  `/bill/*` routes are NOT in the map — they fall through to the
  Render origin and return **HTTP 200 with the app's "Setting Up
  Your Storage" onboarding page** (worse than a 404 — silent
  wrong content). `/static/js/brain.js` 404s via the origin and
  is edge-cached up to 4h. Fix = add the 7 map entries in the
  dashboard worker; exact entries + verification protocol in
  `master-repo/handoffs/2026-11-10-bill-worker-url-map.md`.
  BLOCKED: no headless path to edit the worker — cloudflare MCP
  OAuth grant lacks workers scopes, no API token on this machine,
  dashboard-only source. Needs Brad: dashboard edit, an API
  token, or MCP re-auth.

- **Worker URL-map gap FIXED — all 11 routes + brain.js + 4 images
  live** (devin interactive session, Brad-authorized wrangler OAuth):
  unblocked the headless agent's blocker — `npx wrangler login` → OAuth
  token → `PUT /workers/scripts/bill-mirror/content`. Added the 6
  `PAGES` routes, 5 `ASSETS` entries (`brain.js`, `doc-page.jpeg`,
  `loon.png`, `mn-flag.png`, `semptify-live-001-cover.jpg`), `jpeg`
  content-type. Verified: 11/11 routes 200, assets 200, AI binding
  preserved. **Silent breakage also fixed:** `doc-page.jpeg` paper
  texture, `loon.png`, `mn-flag.png` were 404ing in prod — interior
  pages had no paper texture until this deploy. POST
  `/api/voice-post` → Neon write path proven live (awaiting_review
  3→4); disclosure — probe left a `probe-do-not-post` row in the
  review queue, decline at `/admin/public-voice`. `worker.js` now
  committed to repo (was dashboard-only — the fragility that caused
  this). Docs updated: README + BUILD_GUIDE + BUILD_STATE.

## 2026-11-07

- **"Page at first light" background pass + scene-layering fix** (swe-2,
  task plan-20261106-bill-pages-new-background-design-pass-wh-e453):
  root cause of the "flat empty page" — `.paper-scene` was
  `position:fixed;inset:0;z-index:0`, which paints ABOVE all
  non-positioned content, so the whole liquid frame (header, bill nav,
  tools + options rails) rendered under the parchment and only `main`
  (z-index:1) was visible. pointer-events:none hid it from hit-testing,
  which is why DOM/computed checks looked fine. Scene now sits at
  z-index:-1 — the frame has never visibly rendered until now.
  New interior backdrop: real laid-paper texture (doc-page.jpeg,
  regenerated — the vendored file was an ice-fisherman photo, used as
  card texture on every interior page AND offered on /bill/press as
  "the paper texture") + dawn band rising at the top edge + lamp pool
  + cool water shade + loon woodcut watermark (multiply blend,
  bottom-right) + deckle edge vignette + 80s lamp-glow breathe (off
  under prefers-reduced-motion). Cover /bill: dropped the winter-snow
  cherry photo (season clash, covered the kicker), loon now blends via
  multiply (was a floating white box), flag stays, scene gets the same
  deckle edge vignette. Verified: all 11 routes + 4 scene assets 200,
  IronBee shots at 1440px + 375px, console clean, reduced-motion gate
  confirmed live. NOT pushed — awaiting Brad's visual check.
  Flagged: cherry.jpg now unreferenced (31KB dead asset — delete or
  keep for reuse); at ≤1100px body drops to display:block so rails
  stack in DOM order (tools before main) — pre-existing shell
  behavior, not touched.

- **Verification re-run post-4dbf38d/d7d4f70** (swe-2, same task —
  dispatcher re-spawn): fresh pass on current HEAD. py_compile PASS
  (3.11.9): build.py, sync_assets.py, preview_server.py; brain.js
  `node --check` PASS. build.py clean — drift gate + 11 pages; only
  diff = history.html picking up 2 new canon commits (e3612507,
  9c6061d1), regenerated + committed as usual. pytest
  test_ssot_architecture.py 8/8 PASS (68s, --no-cov; the earlier
  coverage-gate error is an artifact of running one file, not a test
  failure). guardrail_engine 9/9 PASS (86.4s). Manual: preview :8791 —
  19 route/asset probes all 200 (11 pages, brain.js, law-linker.js,
  5 images, /api/voice-posts proxy); IronBee runtime trace on
  /bill/live: every request repo-local /static/* or Google Fonts except
  the voice-posts data seam (200 via proxy), console zero messages,
  ARIA shows all four rails + live-board status text.
- **Verification resubmit pass** (swe-2, same task — desk bounce asked
  for populated verification fields): re-ran everything independently.
  py_compile PASS (3.11.9): build.py, sync_assets.py, preview_server.py.
  build.py clean — drift gate + 11 pages, zero diff vs committed root.
  pytest tests/test_ssot_architecture.py 8/8 PASS (45.32s, venv311).
  guardrail_engine 9/9 PASS (34.34s). Manual: preview_server :8791 —
  16 route/asset probes all 200; IronBee runtime trace on /bill +
  /your-voice: 130 requests all 200, every request repo-local /static/*
  or Google Fonts except the /api/voice-posts data seam (200 via proxy);
  console clean both pages. **Found + fixed:** home.html (tracked legacy
  Semptify Live cover, still served at /home.html) referenced
  /static/img/semptify-live-001-cover.jpg which was never vendored —
  404. Added to sync_assets VERBATIM_FILES and synced; now 200.
  home.html itself is a legacy non-bill page — retire decision logged
  to the queue for Brad.

- **Microsite self-containment audit + worker-map doc fix** (swe-2,
  task plan-20261105-make-bill-section-a-self-contained-micro-06d7):
  verified the site is fully self-contained — `python build.py` clean
  (drift gate + 11 pages, zero diff vs committed root), runtime trace
  on preview:8791 shows only repo-local `/static/*` + Google Fonts +
  the `/api/voice-posts` data seam (200, proxied). No app-shell
  dependency anywhere. Fixed a doc gap: `/static/js/brain.js` was not
  in the README Worker-map contract or the BUILD_STATE deploy
  prerequisite — without a worker entry it would 404 in prod and kill
  the tools/options rails. Added `.gitignore` (`__pycache__/`, `*.log`,
  `nul*`).

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
