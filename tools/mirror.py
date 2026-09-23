#!/usr/bin/env python3
"""Mirror the Webflow-hosted freshconcept.co into this repo as static files.

Fetches each page, downloads every asset it references on Webflow's CDN (plus
assets referenced from the downloaded CSS), stores them under assets/, and
rewrites the CDN URLs to local paths. Re-run to refresh from the live site.
"""
import pathlib
import re
import sys
import urllib.parse
import urllib.request

ORIGIN = "https://www.freshconcept.co"
PAGES = {"/": "index.html", "/pricing": "pricing.html", "/startups": "startups.html",
         "/contact-us": "contact-us.html"}
# Hosts whose files get copied locally, and the local prefix they map to.
HOSTS = {"https://cdn.prod.website-files.com/": "/assets/",
         "https://d3e54v103j8qbb.cloudfront.net/": "/assets/vendor/"}
URL_RE = re.compile("(" + "|".join(re.escape(h) for h in HOSTS) + r")[^\s\"'<>&,]+")

ROOT = pathlib.Path(__file__).resolve().parent.parent
seen = set()


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (mirror)"})
    with urllib.request.urlopen(req) as r:
        return r.read()


def clean(url):
    # Parens are legal in asset names ("logo (1).png"); drop an unbalanced one closing a CSS url().
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1]
    return url


def local_path(url):
    for host, prefix in HOSTS.items():
        if url.startswith(host):
            rel = urllib.parse.unquote(url[len(host):].split("?")[0])
            return ROOT / (prefix.strip("/") + "/" + rel)


def rewrite(text):
    for host, prefix in HOSTS.items():
        text = text.replace(host, prefix)
    return text


def grab(url):
    if url in seen:
        return
    seen.add(url)
    dest = local_path(url)
    try:
        data = fetch(url)
    except urllib.error.HTTPError as e:
        print(f"FAILED {e.code} {url}", file=sys.stderr)
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.suffix == ".css":
        css = data.decode("utf-8")
        for u in sorted({clean(m.group(0)) for m in URL_RE.finditer(css)}):
            grab(u)
        data = rewrite(css).encode("utf-8")
    dest.write_bytes(data)
    print("asset", dest.relative_to(ROOT), file=sys.stderr)


for path, out in PAGES.items():
    html = fetch(ORIGIN + path).decode("utf-8")
    for url in sorted({clean(m.group(0)) for m in URL_RE.finditer(html)}):
        grab(url)
    html = rewrite(html)
    # Internal links that were written as absolute URLs.
    html = html.replace('href="' + ORIGIN + "/", 'href="/')
    (ROOT / out).write_text(html, encoding="utf-8")
    print("page ", out, file=sys.stderr)
