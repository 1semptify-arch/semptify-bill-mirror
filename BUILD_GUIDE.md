# Site Build Guide — semptify.org bill microsite

How the public bill site is built and shipped. Source of truth:
`C:\master-repo\semptify-bill-mirror` (its own repo, independent of the
Semptify app — own layout, nav, stylesheet, build).

## The one-command build

```bash
cd C:\master-repo\semptify-bill-mirror
python build.py
```

Assembles `src/pages/*.html` + `src/partials/*` + `src/bill.css` into the
**root `*.html` files**. Commit the root files after building — they are
what actually ships.

## App-sourced assets stay in sync — enforced

Several root files are verbatim copies of the Semptify app's canonical
assets (`ssot.css`, `northstar.css`, `law-linker.js`, `fetch-helpers.js`,
`narration-strip.js`, `websocket-client.js`, `htmx.min.js`, flags,
lake/bill-scene images), and `src/bill.css` vendors whole sections of
`static/css/ssot-design-system.css`. They used to drift silently.

`build.py` now runs `sync_assets.py --check` first and **fails the build
when any copy is stale**. Refresh with:

```bash
python sync_assets.py          # copy fresh files + splice vendored sections
python sync_assets.py --check  # report drift only, exit 1 if any
python build.py --allow-drift  # bypass the gate (escape hatch)
```

If the checker reports "NEEDS HAND MERGE" on the northstar block, that
part of `src/bill.css` has bill-specific overrides — re-merge that block
by hand from `static/css/themes/northstar.css`.

## How it deploys

- A **Cloudflare Worker** serves the site. It pulls the root `*.html`
  files from this GitHub repo and caches them **~5 minutes**.
- No build step on Cloudflare's side — the repo IS the artifact.
- Push to the repo's main branch = live within ~5 minutes.
- System-wide map (all repos → GitHub → Cloudflare/Render):
  `manuals/semptify-infra-manual.md` in `master-repo`.

## Layout

```
src/
  bill.css            ONE stylesheet — vendored tokens + northstar theme,
                      inlined into every interior page. Pages work from
                      file:// or any host.
  partials/
    head.html         doctype + meta + fonts + {{TITLE}}/{{DESC}}/{{BILL_CSS}}
    nav.html          interior nav (bill links + Semptify exit)
  pages/              per-page content fragments
root *.html           BUILT OUTPUT — commit these, never hand-edit
```

## Rules

- **Never hand-edit root `*.html`** — they are regenerated; edits die on
  the next `build.py` run. Edit `src/` and rebuild.
- Pages must stay self-contained (CSS inlined) — no app dependencies, no
  shared skin with semptify-jsam.onrender.com.
- Dark mode, buttons, badges: follow `ssot-design-system.css` conventions
  already vendored into `bill.css`.

## Verifying a change is live

1. `python build.py` → commit root files → push.
2. Wait ~5 min (worker cache), then load the page in a real browser —
   check dark mode, console errors, mobile width.
3. The app origin (`semptify-jsam.onrender.com/bill*`) must keep 301-ing
   to `semptify.org/bill*` — if it ever serves 200 again, the canonical
   redirect regressed (see `app/modules/portal/pages.py` `redirect_to`).
