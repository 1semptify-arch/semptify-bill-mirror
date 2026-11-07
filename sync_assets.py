#!/usr/bin/env python3
"""sync_assets.py — keep app-sourced static assets in lockstep.

The bill microsite is self-contained, but a set of root files and the
vendored sections inside src/bill.css are copies of canonical files in
the sibling Semptify app repo (../modules/app-semptify-fastapi). They
used to be synced by hand; the copies went stale and the site silently
served outdated CSS (northstar dark-pin + ssot heading fix missing).
This script makes the sync mechanical and checkable.

    python sync_assets.py           # copy fresh files + splice vendored sections
    python sync_assets.py --check   # report drift, write nothing, exit 1 if any

build.py runs the check before every build, so stale assets fail loudly
instead of shipping silently.

Three tiers of tracking:

  VERBATIM_FILES      whole-file copies (css/js/img) — byte-identical.
  VENDORED_SECTIONS   banner-delimited sections of ssot-design-system.css
                      copied verbatim into src/bill.css.
  REQUIRED_BLOCKS     blocks inside files that bill.css merges WITH local
                      edits (the northstar theme section) — the sentinel
                      tail must appear verbatim; can't auto-splice.
"""
import pathlib
import re
import sys

if sys.stdout is not None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).parent
APP_ROOT = ROOT.parent / "modules" / "app-semptify-fastapi"
BILL_CSS = ROOT / "src" / "bill.css"

# (app repo-relative source, mirror root-relative destination)
VERBATIM_FILES = [
    ("static/css/ssot-design-system.css",  "ssot.css"),
    ("static/css/themes/northstar.css",    "northstar.css"),
    ("static/js/law-linker.js",            "law-linker.js"),
    ("static/js/fetch-helpers.js",         "fetch-helpers.js"),
    ("static/js/narration-strip.js",       "narration-strip.js"),
    ("static/js/core/websocket-client.js", "websocket-client.js"),
    ("static/js/htmx.min.js",              "htmx.min.js"),
    ("static/img/flag-mn.svg",             "flag-mn.svg"),
    ("static/img/flag-us.svg",             "flag-us.svg"),
    ("static/img/mn-lake-sunrise.jpg",     "mn-lake-sunrise.jpg"),
    ("static/img/bill-scene-ai.jpg",       "bill-scene-ai.jpg"),
    ("static/img/bill-scene-alt1.jpg",     "bill-scene-alt1.jpg"),
    ("static/img/bill-scene-alt2.jpg",     "bill-scene-alt2.jpg"),
    ("static/img/bill-scene-aurora.jpg",   "bill-scene-aurora.jpg"),
    ("static/img/bill-scene-day.jpg",      "bill-scene-day.jpg"),
]

# Sections of static/css/ssot-design-system.css vendored verbatim into
# src/bill.css, matched by the first title line of each /* ==== */ banner.
# Kept in the order they appear in bill.css. "1. CSS VARIABLES" is special:
# bill.css's own file-header comment stands in for that section's banner.
VENDORED_SECTIONS = [
    "1. CSS VARIABLES",
    "2. RESET & BASE STYLES",
    "TYPE SCALE",
    "3. UTILITY CLASSES",
    "4. COMPONENT CLASSES",
    "6. RESPONSIVE UTILITIES",
    "7. ANIMATIONS",
    "8. ACCESSIBILITY",
    "9. UNIFIED FOOTER",
    "SECTION 10: MAIN NAVIGATION",
    "SITE SHELL v5",
]

# (app repo-relative file, marker comment, description). The text from the
# marker to end-of-file must appear verbatim inside src/bill.css — these are
# merged regions with bill-specific overrides, so only the tail is checked.
REQUIRED_BLOCKS = [
    ("static/css/themes/northstar.css",
     "/* Explicit-theme pin",
     "northstar light-only dark-mode pin"),
]

_BANNER = re.compile(r"(?m)^(?=/\* ={5,})")


def _read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


def _chunks(text: str):
    """Split CSS on banner comments -> list of (title, chunk)."""
    out = []
    for part in _BANNER.split(text):
        title = ""
        for ln in part.splitlines()[1:4]:
            t = ln.strip(" \t*/-")
            if t:
                title = t
                break
        out.append((title, part))
    return out


def _find(chunks, key: str):
    for title, part in chunks:
        if key in title:
            return part
    return None


def _strip_banner(chunk: str) -> str:
    return chunk.split("*/", 1)[1] if "*/" in chunk else chunk


def collect_drift(app_root: pathlib.Path):
    """Return list of drift descriptions; empty means clean.

    Raises FileNotFoundError if the app repo isn't where expected.
    """
    problems = []

    for src_rel, dst_rel in VERBATIM_FILES:
        src, dst = app_root / src_rel, ROOT / dst_rel
        if not src.exists():
            problems.append(f"{dst_rel}: app source missing ({src_rel})")
        elif not dst.exists():
            problems.append(f"{dst_rel}: mirror copy missing")
        elif src.read_bytes() != dst.read_bytes():
            problems.append(f"{dst_rel}: stale copy of app {src_rel}")

    bill = _read(BILL_CSS)
    ssot = _read(app_root / "static/css/ssot-design-system.css")
    bill_chunks = _chunks(bill)
    app_chunks = _chunks(ssot)

    for key in VENDORED_SECTIONS:
        app_part = _find(app_chunks, key)
        if app_part is None:
            problems.append(f"bill.css: app ssot no longer has section '{key}'")
            continue
        if key == "1. CSS VARIABLES":
            # bill.css's file header stands in for this banner — compare
            # bodies (text after the leading comment), not banner text.
            # The header comment itself is a banner-style chunk, so the
            # vars body lives in the first non-empty chunk of the file.
            bill_body = next((_strip_banner(p) for t, p in bill_chunks
                              if p.strip()), "")
            app_body = _strip_banner(app_part)
            if bill_body.strip() != app_body.strip():
                problems.append(
                    f"bill.css: vendored section '{key}' drifted")
        else:
            bill_part = _find(bill_chunks, key)
            if bill_part is None:
                problems.append(f"bill.css: missing vendored section '{key}'")
            elif bill_part != app_part:
                problems.append(f"bill.css: vendored section '{key}' drifted")

    for src_rel, marker, desc in REQUIRED_BLOCKS:
        app_text = _read(app_root / src_rel)
        i = app_text.find(marker)
        if i < 0:
            problems.append(f"{src_rel}: marker '{marker.strip()}' not found")
        elif app_text[i:] not in bill:
            problems.append(f"bill.css: {desc} missing or stale")

    return problems


def sync(app_root: pathlib.Path) -> int:
    problems = collect_drift(app_root)
    if not problems:
        print("sync_assets: everything already in sync")
        return 0

    unfixable = []
    for src_rel, dst_rel in VERBATIM_FILES:
        src, dst = app_root / src_rel, ROOT / dst_rel
        if src.exists() and (not dst.exists()
                             or src.read_bytes() != dst.read_bytes()):
            dst.write_bytes(src.read_bytes())
            print(f"  synced {dst_rel} <- {src_rel}")

    bill = _read(BILL_CSS)
    orig_bill = bill
    ssot = _read(app_root / "static/css/ssot-design-system.css")
    app_chunks = _chunks(ssot)

    for key in VENDORED_SECTIONS:
        app_part = _find(app_chunks, key)
        if app_part is None:
            continue
        if key == "1. CSS VARIABLES":
            # Keep bill.css's own file-header comment; replace the body
            # between it and the next banner with the app's section body.
            # Banner match must be line-anchored — a substring find hits
            # indented comments inside :root.
            hdr_end = bill.find("*/") + 2
            m = _BANNER.search(bill[hdr_end:])
            next_banner = hdr_end + m.start() if m else len(bill)
            new_body = "\n" + _strip_banner(app_part).lstrip("\n")
            if bill[hdr_end:next_banner] != new_body:
                bill = bill[:hdr_end] + new_body + bill[next_banner:]
                print(f"  spliced src/bill.css section '{key}'")
        else:
            bill_chunks = _chunks(bill)
            bill_part = _find(bill_chunks, key)
            if bill_part is not None and bill_part != app_part:
                bill = bill.replace(bill_part, app_part, 1)
                print(f"  spliced src/bill.css section '{key}'")
    if bill != orig_bill:
        BILL_CSS.write_text(bill, encoding="utf-8")

    for src_rel, marker, desc in REQUIRED_BLOCKS:
        app_text = _read(app_root / src_rel)
        i = app_text.find(marker)
        if i >= 0 and app_text[i:] not in bill:
            unfixable.append(f"bill.css: {desc} — re-merge by hand "
                             f"(src/bill.css northstar section has local "
                             f"overrides; copy the block from {src_rel})")

    if unfixable:
        for u in unfixable:
            print(f"  NEEDS HAND MERGE: {u}", file=sys.stderr)
        return 1
    print("sync_assets: all drift resolved — rebuild with python build.py")
    return 0


def check(app_root: pathlib.Path) -> int:
    try:
        problems = collect_drift(app_root)
    except FileNotFoundError:
        print("sync_assets: WARNING app repo not found at "
              f"{app_root} — drift unverifiable", file=sys.stderr)
        return 0
    if not app_root.is_dir():
        print("sync_assets: WARNING app repo not found at "
              f"{app_root} — drift unverifiable", file=sys.stderr)
        return 0
    if problems:
        print("sync_assets: STALE app-sourced assets:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print("run: python sync_assets.py", file=sys.stderr)
        return 1
    print("sync_assets: all app-sourced assets in sync")
    return 0


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--app-root=")]
    app_root = ROOT.parent / "modules" / "app-semptify-fastapi"
    for a in sys.argv[1:]:
        if a.startswith("--app-root="):
            app_root = pathlib.Path(a.split("=", 1)[1])
    if not app_root.is_dir():
        print("sync_assets: WARNING app repo not found at "
              f"{app_root} — nothing to verify against", file=sys.stderr)
        return 0
    if "--check" in args:
        return check(app_root)
    return sync(app_root)


if __name__ == "__main__":
    sys.exit(main())
