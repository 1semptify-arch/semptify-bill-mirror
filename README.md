# The Bill — a self-contained microsite

The public face of the Minnesota Rent Assurance Bill. **This repository is
the source of truth** — the site is authored here, built here, and can live
anywhere. It is deliberately independent of the Semptify web app: own layout,
own navigation, own stylesheet, own build. Same URLs, same pages, no shared
skin.

## Build

```bash
python build.py
```

Assembles `src/pages/*.html` + partials + `src/bill.css` into the root
`*.html` files. **The root files are what the Cloudflare Worker serves** —
commit them after building (the worker pulls root files from the GitHub repo
and caches them ~5 minutes).

The build first runs `sync_assets.py --check`: every file copied or
vendored from the app repo (`ssot.css`, `northstar.css`, shared JS,
images, and `src/bill.css`'s vendored ssot sections) must match its
source or the build fails. Run `python sync_assets.py` to refresh.

## Layout

```
src/
  bill.css            ONE stylesheet. Vendored design tokens + components +
                      northstar theme. No imports. Inlined into every
                      interior page by build.py, so a page works from
                      file:// or any host.
  partials/
    head.html         doctype + meta + fonts + {{TITLE}}/{{DESC}}/{{BILL_CSS}}
    nav.html          interior nav (bill link set + Semptify → exit)
    nav_deck.html     cover topbar variant (same links)
    aside.html        sidebar — identical on every interior page
    foot.html         disclaimer + legal links + law-linker.js + close
    foot_deck.html    cover footer variant + close
  pages/              one fragment per page:
    bill.html         cover — chrome: deck (own palette, cinematic)
    live.html         live draft
    research.html     numbers & sources
    what-the-bill-changes.html
    your-voice.html   board + anonymous post form
    history.html      version history — {{BILL_HISTORY}} slot is filled at
                      build time by build.py's git_log merge (see below)
    providers.html    for housing providers
    brief.html        lawmakers & staff one-pager
    classroom.html    classroom kit
    press.html        press room
    myths.html        myths & facts
```

Page fragments start with a `<!-- -->` front-matter block:

```
<!--
title: Page Title — shown in <title>
desc:  meta description
nav:   bill | live | research | changes | voice   (active link)
chrome: interior | deck
-->
```

`interior` = northstar shell (sky-pale paper, navy ink) + nav + aside +
footer. `deck` = the cover's own look (dawn lake, gold accents) + topbar +
flag footer.

## Build-time slots

- `{{CUR_<key>}}` in the nav partials — `aria-current="page"` for the
  active link, keyed by `nav:` front-matter.
- `{{BILL_HISTORY}}` in `history.html` — `build.py` runs `git log` over the
  bill canon paths in this repo and in the sibling
  `modules/app-semptify-fastapi` checkout (turnbuchalla builder docs,
  public bill templates, claims data), merges them by date, and renders
  one table row per commit linked to GitHub. If the app repo isn't beside
  this one, the build still succeeds — that section renders an honest
  "source unavailable" row instead of failing.

## Design rules that hold this thing together

1. **Zero external stylesheet deps.** Pages may link fonts
   (fonts.googleapis.com) and app API endpoints; nothing else leaves the
   site. `bill.css` is inlined per page — the whole site renders from a
   bare file open.
2. **Light-only palette, pinned.** `body[data-theme="northstar"]` sets
   every token to northstar values in BOTH color schemes — no
   `prefers-color-scheme` flips, deterministic everywhere. Dark-mode
   browsers get the designed light theme, never a broken inversion.
3. **One nav, one link set** (`rail_top.html` / `nav_deck.html` — update
   both, they mirror each other). Task order: Bill → Live draft → The
   numbers → What it changes → Your Voice → Version history →
   For providers → For lawmakers → Classroom kit → Press room →
   Myths & facts → Semptify →.
4. **The seam to Semptify is data-only.** `/api/*` calls (voice posts,
   locale) proxy to the app origin — pipelines may cross, layouts may not.
   Legal pages (/privacy, /terms, …) stay app-side, linked from the footer.
5. **`aria-current="page"`** marks the active nav link — set by `nav:` in
   front-matter, filled by build.py `{{CUR_*}}` slots.

## What the Worker expects (unchanged)

`bill.html` → `/bill`, `live.html` → `/bill/live`,
`research.html` → `/bill/research`, `your-voice.html` → `/your-voice`,
`what-the-bill-changes.html` → `/what-the-bill-changes`,
`history.html` → `/bill/history`, `providers.html` → `/bill/providers`,
`brief.html` → `/bill/brief`, `classroom.html` → `/bill/classroom`,
`press.html` → `/bill/press`, `myths.html` → `/bill/myths`,
`/static/img/*` → root images, `/static/js/*` → root JS files
(`law-linker.js`, `brain.js`), `/api/*` → app origin. Root filenames are
the contract — do not rename pages without updating the Worker map.

## The Worker lives here too

`worker.js` (repo root) is the Cloudflare Worker source — previously
dashboard-only, now versioned here. Its `PAGES` and `ASSETS` maps are the
URL contract: **adding a page or a `/static/*` asset means adding a map
entry here AND redeploying the worker**, or it 404s/redirects wrong in
prod. Deploy:

```bash
# after editing worker.js — multipart upload, preserves bindings
curl -X PUT -H "Authorization: Bearer $CF_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/<account>/workers/scripts/bill-mirror/content" \
  -F 'metadata={"main_module":"worker.js"};type=application/json' \
  -F 'worker.js=@worker.js;type=application/javascript+module'
```

(or `wrangler deploy` with a minimal `wrangler.toml` — name `bill-mirror`,
main `worker.js`, AI binding `AI`). Verify with curl probes on
semptify.org — code deploys instantly; only the GitHub-fetched page
content carries the ~5 min cache.

## If you move it

Copy the root `*.html` + `bill-scene-*.jpg`, `flag-*.svg`,
`law-linker.js` to any static host; rewrite `/static/img|js` and `/api`
paths for the new host (or drop the assets inline). The pages' HTML, CSS,
and nav need nothing else.
