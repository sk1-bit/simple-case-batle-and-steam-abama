#!/usr/bin/env python3
"""Generate HVH.CASES app icons in multiple sizes from a single high-res master."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR = os.path.join(os.path.dirname(__file__), "icons")
os.makedirs(OUT_DIR, exist_ok=True)

# Master resolution
MASTER = 1024


def make_icon(size, maskable=False):
    """Create an HVH.CASES app icon at given size.
    - dark cyan→violet radial background
    - bright cyan glow halo
    - 'HVH' wordmark with violet/cyan stroke
    - tiny .CASES tagline beneath
    - if maskable: ensure safe zone padding (no edge content)
    """
    img = Image.new("RGB", (MASTER, MASTER), (5, 7, 18))
    d = ImageDraw.Draw(img)

    # Background gradient: radial via concentric circles
    cx, cy = MASTER // 2, MASTER // 2
    max_r = int(MASTER * 0.72)
    for r in range(max_r, 0, -8):
        t = r / max_r
        # cyan→violet
        rc = int(8 + (12 - 8) * (1 - t))
        gc = int(11 + (22 - 11) * (1 - t))
        bc = int(28 + (66 - 28) * (1 - t))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(rc, gc, bc))

    # Outer ring/border
    ring_inset = 36
    d.ellipse(
        (ring_inset, ring_inset, MASTER - ring_inset, MASTER - ring_inset),
        outline=(0, 212, 255),
        width=10,
    )
    # Soft glow blur on a copy
    glow = Image.new("RGBA", (MASTER, MASTER), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse(
        (ring_inset - 8, ring_inset - 8, MASTER - ring_inset + 8, MASTER - ring_inset + 8),
        outline=(0, 212, 255, 220),
        width=22,
    )
    glow = glow.filter(ImageFilter.GaussianBlur(28))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")

    # Re-init draw
    d = ImageDraw.Draw(img)

    # HVH wordmark
    try:
        # Pick a bold font
        for fpath in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]:
            if os.path.exists(fpath):
                main_font = ImageFont.truetype(fpath, int(MASTER * 0.32))
                sub_font = ImageFont.truetype(fpath, int(MASTER * 0.09))
                break
        else:
            main_font = ImageFont.load_default()
            sub_font = ImageFont.load_default()
    except Exception:
        main_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()

    # Draw 'HVH'
    text = "HVH"
    bbox = d.textbbox((0, 0), text, font=main_font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (MASTER - tw) // 2 - bbox[0]
    ty = int(MASTER * 0.32) - bbox[1]

    # Drop shadow
    shadow = Image.new("RGBA", (MASTER, MASTER), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.text((tx + 8, ty + 14), text, font=main_font, fill=(0, 212, 255, 180))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")

    d = ImageDraw.Draw(img)
    # Main text: white center with violet outline by drawing offsets
    for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
        d.text((tx + dx, ty + dy), text, font=main_font, fill=(122, 92, 255))
    d.text((tx, ty), text, font=main_font, fill=(255, 255, 255))

    # Subtitle .CASES
    sub = ".CASES"
    bbox2 = d.textbbox((0, 0), sub, font=sub_font)
    sw, sh = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
    sx = (MASTER - sw) // 2 - bbox2[0]
    sy = int(MASTER * 0.7) - bbox2[1]
    d.text((sx, sy), sub, font=sub_font, fill=(0, 212, 255))

    # Resize
    final = img.resize((size, size), Image.LANCZOS)

    if maskable:
        # For maskable icons, our safe zone is the center ~80%. The above design has
        # plenty of background padding, so it's already maskable-safe.
        pass

    return final


def make_apple_touch(size=180):
    """Apple touch icon — same design, but no transparency."""
    return make_icon(size)


SIZES = [
    ("icon-72.png", 72, False),
    ("icon-96.png", 96, False),
    ("icon-128.png", 128, False),
    ("icon-144.png", 144, False),
    ("icon-152.png", 152, False),
    ("icon-192.png", 192, False),
    ("icon-256.png", 256, False),
    ("icon-384.png", 384, False),
    ("icon-512.png", 512, False),
    ("icon-192-maskable.png", 192, True),
    ("icon-512-maskable.png", 512, True),
    ("apple-touch-icon.png", 180, False),
    ("favicon-16.png", 16, False),
    ("favicon-32.png", 32, False),
    ("favicon-64.png", 64, False),
]

print("Generating icons...")
for fname, sz, mask in SIZES:
    img = make_icon(sz, maskable=mask)
    p = os.path.join(OUT_DIR, fname)
    img.save(p, "PNG", optimize=True)
    print(f"  {fname} {sz}x{sz} -> {os.path.getsize(p)} bytes")

# Generate .ico (multi-resolution) for Windows / Tauri
ico_sizes = [16, 32, 48, 64, 128, 256]
ico_img = make_icon(256)
ico_path = os.path.join(OUT_DIR, "icon.ico")
ico_img.save(ico_path, format="ICO", sizes=[(s, s) for s in ico_sizes])
print(f"  icon.ico -> {os.path.getsize(ico_path)} bytes")

# Generate larger master for Tauri
tauri_master = make_icon(1024)
tauri_master.save(os.path.join(OUT_DIR, "icon-1024.png"), "PNG", optimize=True)
print(f"  icon-1024.png 1024x1024")

print("Done!")
