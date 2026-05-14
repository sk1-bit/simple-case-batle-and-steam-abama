#!/usr/bin/env python3
"""Idempotently inject Phase 11 (Game Shop) module into hvh-app/public/index.html."""
import re
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parent
HTML = WORK / "hvh-app" / "public" / "index.html"
MOD = WORK / "_phase11_gameshop.html"


def main() -> None:
    if not HTML.exists():
        print(f"ERROR: {HTML} not found", file=sys.stderr)
        sys.exit(1)
    if not MOD.exists():
        print(f"ERROR: {MOD} not found", file=sys.stderr)
        sys.exit(1)

    html = HTML.read_text(encoding="utf-8")
    module = MOD.read_text(encoding="utf-8")

    # 1) Strip any existing PHASE11 block
    pattern = re.compile(
        r"\n?<!--\s*PHASE11_CSS_START\s*-->.*?<!--\s*PHASE11_JS_END\s*-->\n?",
        re.DOTALL,
    )
    new_html, n = pattern.subn("\n", html)
    if n:
        print(f"Removed {n} existing PHASE11 block(s).")

    # 2) Determine insertion point: after PHASE10_JS_END if present, else before </body>
    p10_end = new_html.find("<!-- PHASE10_JS_END -->")
    if p10_end != -1:
        line_end = new_html.find("\n", p10_end)
        if line_end == -1:
            line_end = p10_end + len("<!-- PHASE10_JS_END -->")
        insert_at = line_end + 1
        prefix = new_html[:insert_at]
        suffix = new_html[insert_at:]
        new_html = prefix + "\n" + module.rstrip() + "\n" + suffix
        print("Inserted Phase 11 after PHASE10_JS_END marker.")
    else:
        body_close = new_html.rfind("</body>")
        if body_close == -1:
            print("ERROR: neither PHASE10_JS_END marker nor </body> found", file=sys.stderr)
            sys.exit(1)
        new_html = new_html[:body_close] + "\n" + module.rstrip() + "\n" + new_html[body_close:]
        print("Inserted Phase 11 before </body>.")

    HTML.write_text(new_html, encoding="utf-8")
    size = HTML.stat().st_size
    lines = new_html.count("\n") + 1
    markers = new_html.count("PHASE11_")
    print(f"Wrote {HTML}: {size:,} bytes, {lines:,} lines, {markers} PHASE11 marker(s).")


if __name__ == "__main__":
    main()
