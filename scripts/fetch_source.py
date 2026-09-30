#!/usr/bin/env python3
"""Read-only direct read of a monitored source (access: "curl" in data/sources.json).

Usage: python3 scripts/fetch_source.py URL [--max-chars N]

Rules enforced here (see CLAUDE.md, "Zdroje"):
- URL host must belong to an active source with access "curl" in data/sources.json.
- robots.txt of the host must allow our user agent.
- One plain GET with an honest user agent. No retries with another UA, no cookies,
  no mirrors or caches. A bot challenge / 4xx / 5xx = source unavailable.

Output: header lines (URL, HTTP status, time, og:*/meta tags) followed by page text.
Exit codes: 0 = direct read OK, 2 = not allowed / unavailable (use WebSearch instead).
"""
import json
import re
import sys
import urllib.error
import urllib.request
import urllib.robotparser
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
UA = "FZ1073-monitor/1.0 (+https://github.com/tomasdrobnik/News_agregator)"
TIMEOUT = 25
CHALLENGE = re.compile(r"just a moment|cf-chl|challenge-platform|captcha|access denied|are you a robot", re.I)
META_KEYS = ("og:title", "og:image", "og:url", "twitter:image", "description",
             "article:published_time", "article:modified_time", "author")


def fail(msg):
    print(f"UNAVAILABLE: {msg}")
    print("→ Obsah nebyl přímo přečten. Použij WebSearch a v záznamu to uveď.")
    sys.exit(2)


def host(url):
    h = (urlsplit(url).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def allowed_source(url):
    sources = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))["sources"]
    h = host(url)
    for s in sources:
        sh = host(s["url"])
        if s.get("active") and s.get("access") == "curl" and (h == sh or h.endswith("." + sh)):
            return s
    return None


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/xml,text/plain;q=0.9,*/*;q=0.5"})
    return urllib.request.urlopen(req, timeout=TIMEOUT)


def robots_ok(url):
    parts = urlsplit(url)
    rp = urllib.robotparser.RobotFileParser()
    try:
        with get(f"{parts.scheme}://{parts.netloc}/robots.txt") as r:
            rp.parse(r.read().decode("utf-8", "replace").splitlines())
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            fail(f"robots.txt webu {host(url)} vrací HTTP {e.code} (blokace botů)")
        rp.parse([])      # 404 etc. → no restrictions
    except Exception as e:
        fail(f"robots.txt nelze načíst ({e})")
    return rp.can_fetch(UA, url)


class Page(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "nav", "footer", "header", "form"}

    def __init__(self):
        super().__init__()
        self.meta, self.title, self.text, self.skip, self.in_title = {}, "", [], 0, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.SKIP:
            self.skip += 1
        elif tag == "title":
            self.in_title = True
        elif tag == "meta":
            k = (a.get("property") or a.get("name") or "").lower()
            if k in META_KEYS and a.get("content") and k not in self.meta:
                self.meta[k] = a["content"].strip()
        elif tag in ("p", "br", "li", "h1", "h2", "h3", "h4", "tr", "div"):
            self.text.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        elif tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif not self.skip:
            self.text.append(data)


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        print(__doc__)
        sys.exit(1)
    url = args[0]
    max_chars = int(args[args.index("--max-chars") + 1]) if "--max-chars" in args else 15000
    if urlsplit(url).scheme not in ("http", "https"):
        fail("jen http(s) URL")
    src = allowed_source(url)
    if not src:
        fail(f"{host(url)} není aktivní zdroj s access \"curl\" v data/sources.json")
    if not robots_ok(url):
        fail(f"robots.txt webu {host(url)} automatické čtení zakazuje")
    try:
        with get(url) as r:
            status, final, headers = r.status, r.geturl(), r.headers
            body = r.read(3_000_000).decode(r.headers.get_content_charset() or "utf-8", "replace")
    except urllib.error.HTTPError as e:
        fail(f"HTTP {e.code}" + (" (bot challenge)" if e.headers.get("cf-mitigated") else ""))
    except Exception as e:
        fail(f"spojení selhalo ({e})")
    if headers.get("cf-mitigated") or CHALLENGE.search(body[:20000]) and len(body) < 30000:
        fail("stránka vrátila ochranu proti botům (challenge)")
    if host(final) != host(url) and not allowed_source(final):
        fail(f"přesměrováno mimo registr: {final}")

    p = Page()
    p.feed(body)
    text = re.sub(r"[ \t\r\f\v]+", " ", "".join(p.text))
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
    if len(text) < 200:
        fail("stránka bez čitelného obsahu (vyžaduje JavaScript nebo mezistránku)")
    print(f"DIRECT READ OK – zdroj: {src['name']}")
    print(f"url: {final}")
    print(f"http: {status}")
    print(f"fetched_at: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print(f"title: {' '.join(p.title.split())}")
    for k in META_KEYS:
        if k in p.meta:
            print(f"{k}: {p.meta[k]}")
    print("---")
    print(text[:max_chars] + ("\n[…zkráceno]" if len(text) > max_chars else ""))


if __name__ == "__main__":
    main()
