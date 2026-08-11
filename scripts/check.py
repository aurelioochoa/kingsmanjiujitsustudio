#!/usr/bin/env python3
"""Verify a served Kingsman site.

Usage:
    python3 check.py [BASE_URL]   # default http://127.0.0.1:8091

Checks the home page AND every linked class page (pages/clases/*.html):
- every local asset referenced (js/css/img/video) returns 200, resolved
  correctly against the PAGE's document directory (catches ../ mismatches)
- every internal .html link resolves
- SEO tags present on each page (title, canonical, og:title, description)
- any JSON-LD blocks parse (@type present on home)
Exits non-zero on any failure.
"""
import json
import re
import sys
import urllib.request
from urllib.parse import urljoin, urlparse

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8091"
ROOT = BASE.rstrip("/") + "/"


def fetch_url(url: str):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.status, r.read().decode("utf-8", "replace")


def local_refs(html: str):
    return {
        m for m in re.findall(r'(?:src|href)="([^"]+)"', html)
        if not m.startswith(("#", "http", "//", "data:", "mailto:", "tel:"))
    }


def check_page(url: str, failures: list) -> None:
    try:
        code, html = fetch_url(url)
    except Exception as e:
        failures.append(f"{url} -> {type(e).__name__}: {e}")
        return
    if code != 200:
        failures.append(f"{url} -> HTTP {code}")
        return

    for r in sorted(local_refs(html)):
        target = urljoin(url, r)
        if urlparse(target).netloc != urlparse(url).netloc:
            continue  # resolved to another host — skip
        try:
            c, _ = fetch_url(target)
            if c != 200:
                failures.append(f"{target} ({r}) -> HTTP {c}")
        except Exception as e:
            failures.append(f"{target} ({r}) -> {type(e).__name__}: {e}")

    for tag in ['rel="canonical"', 'property="og:title"', 'name="twitter:card"']:
        if tag not in html:
            failures.append(f"{url}: missing {tag}")
    if re.search(r"<meta name=\"description\"", html) is None:
        failures.append(f"{url}: missing meta description")
    if re.search(r"<title>", html) is None:
        failures.append(f"{url}: missing <title>")

    for i, b in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)):
        try:
            d = json.loads(b)
            if "@type" not in d:
                failures.append(f"{url}: JSON-LD #{i} missing @type")
        except json.JSONDecodeError as e:
            failures.append(f"{url}: JSON-LD #{i} does not parse: {e}")


def main() -> int:
    failures = []
    home_url = urljoin(ROOT, "index.html")
    _, home_html = fetch_url(home_url)

    pages = {home_url}
    for r in local_refs(home_html):
        if r.endswith(".html"):
            pages.add(urljoin(home_url, r))  # class pages found via links

    for p in sorted(pages):
        check_page(p, failures)
        print("checked", p)

    if failures:
        print(f"\nFAIL ({len(failures)}):")
        for f in failures:
            print("  -", f)
        return 1
    print(f"\nOK — {len(pages)} pages, all assets 200 (page-relative), SEO tags + JSON-LD valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())