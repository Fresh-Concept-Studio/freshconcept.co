#!/usr/bin/env python3
"""Build pages that aren't on Webflow, reusing the mirrored site's nav, footer and scripts.

Run after tools/mirror.py, since the shell is taken from contact-us.html. Also refreshes the
embed's gallery thumbnails and copies its images into utah-cancer/images/.
"""
import html
import pathlib
import re
import shutil

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
EMBED = pathlib.Path("/Users/kyle/Develop/utah-cancer/creative-department-embed")
THUMB_WIDTH = 800  # Cards and gallery tiles are at most ~400 CSS px wide; 800 covers 2x screens.


def refresh_thumbs():
    src_dir = EMBED / "images"
    thumbs = src_dir / "thumbs"
    thumbs.mkdir(exist_ok=True)
    for f in sorted(src_dir.glob("*.webp")):
        t = thumbs / f.name
        if t.exists() and t.stat().st_mtime >= f.stat().st_mtime:
            continue
        im = Image.open(f)
        if im.width > THUMB_WIDTH:
            im = im.resize((THUMB_WIDTH, round(im.height * THUMB_WIDTH / im.width)), Image.LANCZOS)
        im.save(t, "WEBP", quality=82, method=6)
        print("thumb", t.name)
    dest = ROOT / "utah-cancer" / "images"
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(src_dir, dest, ignore=shutil.ignore_patterns(".DS_Store"))

shell = (ROOT / "contact-us.html").read_text(encoding="utf-8")
head, body = shell.split("<body", 1)
body = "<body" + body
nav_end = body.index('<div class="section-small')
footer_start = body.index('<footer class="section-footer">')


def page(title, description, content, path, keep_cta=True, site_chrome=True):
    h = head
    h = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", h)
    for attr in ('name="description"', 'property="og:description"', 'property="twitter:description"'):
        h = re.sub(r'<meta content="[^"]*" ' + attr, f'<meta content="{html.escape(description)}" ' + attr, h)
    for attr in ('property="og:title"', 'property="twitter:title"'):
        h = re.sub(r'<meta content="[^"]*" ' + attr, f'<meta content="{html.escape(title)}" ' + attr, h)
    # Neither generated page should be indexed.
    h = h.replace("</title>", '</title><meta name="robots" content="noindex"/>', 1)
    cta = body[body.index('<div class="cta">'):footer_start] if keep_cta else ""
    if site_chrome:
        out = h + body[:nav_end] + content + cta + body[footer_start:]
    else:
        # Standalone page: no nav, footer or Webflow scripts.
        out = h + body[:body.index(">") + 1] + content + "</body></html>"
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    print("built", path)


page("Page not found | Fresh Concept",
     "The page you're looking for doesn't exist or has moved.",
     '<div class="section-small auto-h"><div class="container" style="display:flex;padding:120px 0;text-align:center;flex-direction:column;align-items:center;gap:24px">'
     '<h1 style="color:#fff">Page not found</h1><p style="color:rgba(255,255,255,.7)">The page you\'re looking for doesn\'t exist or has moved.</p>'
     '<a href="/" class="button-secondary w-inline-block"><div class="text-block">Back to home</div></a></div></div>',
     "404.html")

refresh_thumbs()
page("Creative Department | Fresh Concept × Utah Cancer Specialists",
     "Creative Department retainer options for Utah Cancer Specialists.",
     (EMBED / "creative-department.html").read_text(encoding="utf-8"),
     "utah-cancer/index.html", site_chrome=False)
