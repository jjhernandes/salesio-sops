#!/usr/bin/env python3
"""Make a call-recording thumbnail + Slack-preview redirect page.

Usage:
  python3 tools/make_card.py <call_id> "<title>" "<subtitle>" <fathom_url>

Writes cards/<call_id>.png (1200x630) and rec/<call_id>.html. The HTML page
carries og:image tags so Slack shows the thumbnail, then redirects to Fathom.
Live link: https://jjhernandes.github.io/salesio-sops/rec/<call_id>.html
"""
import html
import os
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "tools", "fonts")
BASE = "https://jjhernandes.github.io/salesio-sops"
W, H = 1200, 630
ACCENT = (226, 207, 168)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def make_png(call_id, title, subtitle):
    img = Image.new("RGB", (W, H), (9, 9, 8))
    d = ImageDraw.Draw(img)
    # soft accent glow, top left
    for r in range(420, 0, -6):
        a = int(18 * (1 - r / 420))
        d.ellipse([-r + 120, -r + 80, r + 120, r + 80], fill=(9 + a, 9 + a, 8 + a))

    logo = Image.open(os.path.join(ROOT, "salesio-icon.png")).convert("RGB").resize((88, 88))
    img.paste(logo, (64, 60))
    d.text((170, 78), "SALES.IO  ·  CALL RECORDING", font=font("Inter-Bold.ttf", 26), fill=ACCENT)

    # title, wrapped to 2-3 lines
    tf = font("Inter-Black.ttf", 72)
    lines = textwrap.wrap(title, width=24)[:3]
    if len(textwrap.wrap(title, width=24)) > 3:
        lines[-1] = lines[-1].rstrip(" .,") + "..."
    y = 210
    for line in lines:
        d.text((64, y), line, font=tf, fill=(240, 236, 228))
        y += 86

    d.text((64, H - 96), subtitle, font=font("Inter-Medium.ttf", 30), fill=(138, 132, 117))

    # play button, right side
    cx, cy, R = W - 150, H - 140, 62
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=ACCENT)
    d.polygon([(cx - 18, cy - 28), (cx - 18, cy + 28), (cx + 30, cy)], fill=(9, 9, 8))

    path = os.path.join(ROOT, "cards", f"{call_id}.png")
    img.save(path, optimize=True)
    return path


def make_html(call_id, title, subtitle, fathom_url):
    t, s, u = html.escape(title), html.escape(subtitle), html.escape(fathom_url)
    img = f"{BASE}/cards/{call_id}.png"
    page = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<title>{t}</title>
<meta property="og:type" content="video.other">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{s} · Watch the recording">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="{BASE}/rec/{call_id}.html">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{img}">
<meta http-equiv="refresh" content="0; url={u}">
<style>body{{background:#090908;color:#f0ece4;font-family:-apple-system,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}}a{{color:#e2cfa8}}</style>
</head><body><p>Opening the recording... <a href="{u}">Click here if it doesn't open</a>.</p>
<script>location.replace({fathom_url!r});</script>
</body></html>
"""
    path = os.path.join(ROOT, "rec", f"{call_id}.html")
    with open(path, "w") as f:
        f.write(page)
    return path


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    cid, title, sub, url = sys.argv[1:]
    print(make_png(cid, title, sub))
    print(make_html(cid, title, sub, url))
    print(f"{BASE}/rec/{cid}.html")
