#!/usr/bin/env python3
"""Generate Android launcher icons in mipmap densities."""
import os
from PIL import Image

SRC = "/home/ubuntu/work/hvh-app/icons/icon-1024.png"
DST = "/home/ubuntu/work/hvh-app/cap-android/android/app/src/main/res"

# Standard Android launcher densities for ic_launcher (square)
densities = {
    "mipmap-mdpi": 48,
    "mipmap-hdpi": 72,
    "mipmap-xhdpi": 96,
    "mipmap-xxhdpi": 144,
    "mipmap-xxxhdpi": 192,
}

# Round icon (same size, different file)
src = Image.open(SRC).convert("RGBA")

for d, sz in densities.items():
    folder = os.path.join(DST, d)
    os.makedirs(folder, exist_ok=True)
    resized = src.resize((sz, sz), Image.LANCZOS)
    resized.save(os.path.join(folder, "ic_launcher.png"), "PNG", optimize=True)
    resized.save(os.path.join(folder, "ic_launcher_round.png"), "PNG", optimize=True)
    # foreground for adaptive icon (108dp sized — for densities x4=432px etc)
    adaptive_sz = int(sz * 108 / 48)  # 108dp at each density
    fg = src.resize((adaptive_sz, adaptive_sz), Image.LANCZOS)
    fg.save(os.path.join(folder, "ic_launcher_foreground.png"), "PNG", optimize=True)
    print(f"{d}: {sz}x{sz} icon, {adaptive_sz}x{adaptive_sz} foreground")

# Splash screen — large centered logo on dark
splash_src = Image.new("RGBA", (1280, 1280), (10, 12, 26, 255))
logo = src.resize((640, 640), Image.LANCZOS)
splash_src.paste(logo, (320, 320), logo)
splash_dst_folders = ["drawable", "drawable-port-mdpi", "drawable-port-hdpi", "drawable-port-xhdpi", "drawable-port-xxhdpi", "drawable-port-xxxhdpi", "drawable-land-mdpi", "drawable-land-hdpi", "drawable-land-xhdpi", "drawable-land-xxhdpi", "drawable-land-xxxhdpi"]
for f in splash_dst_folders:
    folder = os.path.join(DST, f)
    os.makedirs(folder, exist_ok=True)
    splash_src.save(os.path.join(folder, "splash.png"), "PNG", optimize=True)
print("splash.png installed in all drawable folders")
