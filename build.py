#!/usr/bin/env python3
"""
build.py — assemble The Bill microsite from src/ into repo-root HTML.

The Cloudflare Worker maps URL paths to these root files, so output lands
at the repo root (NOT dist/). Run after editing anything under src/:

    python build.py

Before assembling pages, the build verifies app-sourced static assets
(root css/js/img copies + the vendored sections inside src/bill.css) are
in sync with ../modules/app-semptify-fastapi via sync_assets.py --check.
Stale assets fail the build — run `python sync_assets.py` to refresh, or
`python build.py --allow-drift` to bypass.

Source layout:
    src/bill.css            single vendored stylesheet, inlined into interior pages
    src/partials/head.html  doctype + head (TITLE/DESC/BILL_CSS slots)
    src/partials/nav.html   interior chrome nav (CUR_<key> slots)
    src/partials/nav_deck   cover-page topbar variant (same link set)
    src/partials/aside.html unified sidebar
    src/partials/foot.html  interior footer + scripts + close
    src/partials/foot_deck  cover footer variant + close
    src/pages/*.html        page fragments with a <!-- ... --> front-matter
                            block: title / desc / nav / chrome

chrome: interior -> shell+nav+aside+footer, bill.css inlined in <style>
        deck     -> standalone cover (own palette/styles, topbar nav,
                    deck footer); bill.css NOT inlined
"""
import datetime
import html
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
PAGES = SRC / "pages"
PARTIALS = SRC / "partials"

BODY_OPEN = {
    "interior": '<body class="shell bill-section" data-theme="northstar">\n',
    "deck":     "<body>\n",
}
NAV_FOR = {"interior": "nav.html", "deck": "nav_deck.html"}
FOOT_FOR = {"interior": "foot.html", "deck": "foot_deck.html"}


def read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


def parse_fragment(text: str):
    m = re.match(r"\s*<!--(.*?)-->", text, re.S)
    if not m:
        raise ValueError("fragment missing front-matter comment")
    meta = {}
    for line in m.group(1).strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    for req in ("title", "desc", "nav", "chrome"):
        if req not in meta:
            raise ValueError(f"fragment missing '{req}' in front-matter")
    return meta, text[m.end():].strip()


NAV_KEYS = ("bill", "live", "research", "changes", "voice",
            "history", "providers", "brief", "classroom", "press", "myths")


def fill_nav(nav_html: str, active: str) -> str:
    for key in NAV_KEYS:
        mark = ' aria-current="page"' if key == active else ""
        nav_html = nav_html.replace("{{CUR_%s}}" % key, mark)
    return nav_html


# Version history — the public change log, generated from git at build time.
# Each entry: (label, repo dir, commit-url base, paths to log).
# The bill draft's canon lives in the sibling Semptify app checkout; if that
# repo isn't beside this one its rows just don't appear (with a note).
HISTORY_SOURCES = [
    ("bill site",
     ROOT,
     "https://github.com/1semptify-arch/semptify-bill-mirror/commit/",
     ["src/", "build.py", "brain.js", "preview_server.py"]),
    ("bill draft &amp; canon",
     ROOT.parent / "modules" / "app-semptify-fastapi",
     "https://github.com/1semptify-arch/Semptify/commit/",
     ["app/static/turnbuchalla/",
      "app/templates/public/bill_draft.html",
      "app/templates/public/bill_hub.html",
      "app/templates/public/bill_live.html",
      "app/templates/public/bill_research.html",
      "app/templates/public/what_the_bill_changes.html",
      "data/bill_claims_public.json"]),
]
HISTORY_LIMIT = 60


def _git_log(repo: pathlib.Path, paths):
    cmd = (["git", "-C", str(repo), "log", "--all",
            "--format=%aI%x09%h%x09%s", "--"] + paths)
    out = subprocess.run(cmd, capture_output=True, text=True,
                         encoding="utf-8", errors="replace",
                         timeout=30)
    if out.returncode != 0:
        return []
    rows = []
    for line in out.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) == 3:
            rows.append(parts)
    return rows


def bill_history() -> str:
    """Merged, dated git history of the bill canon -> <tr> rows."""
    entries = []
    missing = []
    for label, repo, base, paths in HISTORY_SOURCES:
        if not repo.is_dir():
            missing.append(label)
            continue
        try:
            for iso, short, subj in _git_log(repo, paths):
                entries.append((iso, label, short, subj, base))
        except (OSError, subprocess.SubprocessError):
            missing.append(label)

    def sortkey(e):
        try:
            return datetime.datetime.fromisoformat(
                e[0].replace("Z", "+00:00")).timestamp()
        except ValueError:
            return 0.0

    entries.sort(key=sortkey, reverse=True)
    rows = []
    for iso, label, short, subj, base in entries[:HISTORY_LIMIT]:
        rows.append(
            '<tr><td class="vh-date">%s</td>'
            '<td class="vh-repo">%s</td>'
            '<td class="vh-msg">%s</td>'
            '<td class="vh-hash"><a href="%s%s">%s</a></td></tr>' % (
                html.escape(iso[:10]), label,
                html.escape(subj),
                base, html.escape(short), html.escape(short)))
    for label in missing:
        rows.append(
            '<tr><td colspan="4" class="vh-msg"><em>History source '
            "unavailable in this build: %s — the record lives in the "
            "public repos.</em></td></tr>" % label)
    if not rows:
        rows.append(
            '<tr><td colspan="4" class="vh-msg"><em>Git history not '
            "available in this build — the record lives in the public "
            "repos.</em></td></tr>")
    return "\n        ".join(rows)


def build_page(path: pathlib.Path, bill_css: str) -> str:
    meta, body = parse_fragment(read(path))
    if "{{BILL_HISTORY}}" in body:
        body = body.replace("{{BILL_HISTORY}}", bill_history())
    chrome = meta["chrome"]
    if chrome not in BODY_OPEN:
        raise ValueError(f"{path.name}: unknown chrome '{chrome}'")

    head = read(PARTIALS / "head.html")
    head = head.replace("{{TITLE}}", meta["title"])
    head = head.replace("{{DESC}}", meta["desc"])
    head = head.replace("{{BILL_CSS}}",
                        "<style>\n" + bill_css + "\n</style>" if chrome == "interior" else "")

    nav = fill_nav(read(PARTIALS / NAV_FOR[chrome]), meta["nav"])
    if chrome == "interior":
        scene = read(PARTIALS / "scene.html")
        rail_top = fill_nav(read(PARTIALS / "rail_top.html"), meta["nav"])
        rail_tools = read(PARTIALS / "rail_tools.html")
        aside = read(PARTIALS / "aside.html")
    else:
        scene = rail_top = rail_tools = aside = ""
    foot = read(PARTIALS / FOOT_FOR[chrome])

    return "\n".join([head, BODY_OPEN[chrome], scene, nav, rail_top, rail_tools,
                      "", body, "", aside, foot]).rstrip() + "\n"


def main() -> int:
    # Drift gate — app-sourced assets (root css/js/img copies + vendored
    # bill.css sections) must match the app repo or the build fails loudly.
    # Bypass with --allow-drift; refresh copies with sync_assets.py.
    if "--allow-drift" not in sys.argv:
        import sync_assets
        rc = sync_assets.check(sync_assets.APP_ROOT)
        if rc:
            return rc
    bill_css = read(SRC / "bill.css")
    pages = sorted(PAGES.glob("*.html"))
    if not pages:
        print("no pages under src/pages/", file=sys.stderr)
        return 1
    for p in pages:
        out = ROOT / p.name
        html = build_page(p, bill_css)
        out.write_text(html, encoding="utf-8")
        print(f"built {p.name:28s} -> {out.name} ({len(html):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
