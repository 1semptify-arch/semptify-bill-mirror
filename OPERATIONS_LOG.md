# Site Operations Log — semptify.org

Dated record of site-affecting operations. Newest first. Format:
`YYYY-MM-DD — what changed — where verified`.

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
