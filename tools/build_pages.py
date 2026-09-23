#!/usr/bin/env python3
"""Build pages that aren't on Webflow, reusing the mirrored site's nav, footer and scripts.

Run after tools/mirror.py, since the shell is taken from contact-us.html.
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
EMBED = pathlib.Path("/Users/kyle/Develop/utah-cancer/creative-department-embed")

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

page("Creative Department | Fresh Concept × Utah Cancer Specialists",
     "Creative Department retainer options for Utah Cancer Specialists.",
     (EMBED / "creative-department.html").read_text(encoding="utf-8"),
     "utah-cancer/index.html", site_chrome=False)
