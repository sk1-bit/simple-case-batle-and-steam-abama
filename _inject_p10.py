#!/usr/bin/env python3
"""Idempotently inject Phase 10 module into hvh-app/public/index.html.

Removes any existing PHASE10 block (delimited by PHASE10_CSS_START/PHASE10_JS_END
markers), then inserts the freshly-read _phase10_games.html between the
PHASE9_JS_END marker (or </body> as fallback) and the end of the file.
"""
import re
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
HTML = WORK / "hvh-app" / "public" / "index.html"
MOD = WORK / "_phase10_games.html"


def main():
    if not HTML.exists():
        print(f"ERROR: {HTML} not found", file=sys.stderr); sys.exit(1)
    if not MOD.exists():
        print(f"ERROR: {MOD} not found", file=sys.stderr); sys.exit(1)

    html = HTML.read_text(encoding="utf-8")
    module = MOD.read_text(encoding="utf-8")

    # 1) Strip any existing PHASE10 block (between CSS_START and JS_END markers)
    pattern = re.compile(
        r"\n?<!--\s*PHASE10_CSS_START\s*-->.*?<!--\s*PHASE10_JS_END\s*-->\n?",
        re.DOTALL,
    )
    new_html, n = pattern.subn("\n", html)
    if n:
        print(f"Removed {n} existing PHASE10 block(s).")

    # 2) Determine insertion point — prefer right after PHASE9_JS_END marker
    p9_end = new_html.find("<!-- PHASE9_JS_END -->")
    if p9_end != -1:
        # insert after the marker + newline
        line_end = new_html.find("\n", p9_end)
        if line_end == -1:
            line_end = p9_end + len("<!-- PHASE9_JS_END -->")
        insert_at = line_end + 1
        prefix = new_html[:insert_at]
        suffix = new_html[insert_at:]
        new_html = prefix + "\n" + module.rstrip() + "\n" + suffix
        print("Inserted Phase 10 after PHASE9_JS_END marker.")
    else:
        # fallback: insert before </body>
        body_close = new_html.rfind("</body>")
        if body_close == -1:
            print("ERROR: neither PHASE9_JS_END marker nor </body> tag found", file=sys.stderr)
            sys.exit(1)
        new_html = new_html[:body_close] + "\n" + module.rstrip() + "\n" + new_html[body_close:]
        print("Inserted Phase 10 before </body>.")

    HTML.write_text(new_html, encoding="utf-8")
    size = HTML.stat().st_size
    lines = new_html.count("\n") + 1
    markers = new_html.count("PHASE10_")
    print(f"Wrote {HTML}: {size:,} bytes, {lines:,} lines, {markers} PHASE10 marker(s).")


if __name__ == "__main__":
    main()
