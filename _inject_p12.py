#!/usr/bin/env python3
"""Idempotent injector for Phase 12 — Real Imagery layer.

Strips any prior Phase 12 block and re-inserts the latest one right
before </body>, after the Phase 11 block.
"""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
TARGET = (ROOT / "hvh-app" / "public" / "index.html").resolve()
PAYLOAD = (ROOT / "_phase12_images.html").resolve()


def main() -> None:
    html = TARGET.read_text(encoding="utf-8")

    # Strip any existing Phase 12 block (between CSS_START and JS_END markers)
    pattern = re.compile(
        r"\n?<!--\s*PHASE12_CSS_START\s*-->.*?<!--\s*PHASE12_JS_END\s*-->\n?",
        re.DOTALL,
    )
    new_html, n = pattern.subn("\n", html)
    if n:
        print(f"[p12] stripped {n} prior Phase 12 block(s)")

    payload = PAYLOAD.read_text(encoding="utf-8").rstrip() + "\n"

    # Prefer inserting after Phase 11 marker, else fall back to </body>
    anchor = "<!-- PHASE11_JS_END -->"
    idx = new_html.find(anchor)
    if idx != -1:
        insert_at = idx + len(anchor)
        out = new_html[:insert_at] + "\n" + payload + new_html[insert_at:]
        print(f"[p12] injected after {anchor}")
    else:
        body_close = new_html.rfind("</body>")
        if body_close == -1:
            raise SystemExit("Could not find </body> in target HTML")
        out = new_html[:body_close] + payload + new_html[body_close:]
        print("[p12] injected before </body>")

    TARGET.write_text(out, encoding="utf-8")
    print(f"[p12] wrote {len(out)} bytes -> {TARGET}")


if __name__ == "__main__":
    main()
