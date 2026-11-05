#!/usr/bin/env python3
"""
build.py — assemble The Bill microsite from src/ into repo-root HTML.

The Cloudflare Worker maps URL paths to these root files, so output lands
at the repo root (NOT dist/). Run after editing anything under src/:

    python build.py

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
import pathlib
import re
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


def fill_nav(nav_html: str, active: str) -> str:
    for key in ("bill", "live", "research", "changes", "voice"):
        mark = ' aria-current="page"' if key == active else ""
        nav_html = nav_html.replace("{{CUR_%s}}" % key, mark)
    return nav_html


def build_page(path: pathlib.Path, bill_css: str) -> str:
    meta, body = parse_fragment(read(path))
    chrome = meta["chrome"]
    if chrome not in BODY_OPEN:
        raise ValueError(f"{path.name}: unknown chrome '{chrome}'")

    head = read(PARTIALS / "head.html")
    head = head.replace("{{TITLE}}", meta["title"])
    head = head.replace("{{DESC}}", meta["desc"])
    head = head.replace("{{BILL_CSS}}",
                        "<style>\n" + bill_css + "\n</style>" if chrome == "interior" else "")

    nav = fill_nav(read(PARTIALS / NAV_FOR[chrome]), meta["nav"])
    aside = read(PARTIALS / "aside.html") if chrome == "interior" else ""
    foot = read(PARTIALS / FOOT_FOR[chrome])

    return "\n".join([head, BODY_OPEN[chrome], nav, "", body, "", aside, foot]).rstrip() + "\n"


def main() -> int:
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
