#!/usr/bin/env python3
"""Validate data/updates.json and regenerate feed.xml (RSS 2.0).

Usage:  python3 scripts/build_feed.py
Reads site URL from config.json ("site_url"). Exits non-zero on invalid data,
so a broken update never gets committed.
"""
import json
import re
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "updates.json"
FEED = ROOT / "feed.xml"
CONFIG = ROOT / "config.json"

STATUSES = {"official": "Oficiální", "data": "Data", "reported": "Média", "unconfirmed": "Neověřeno"}
REQUIRED = ("id", "found_at", "source", "url", "title", "text", "status")


def parse(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc)


TRACKING = re.compile(r"^(utm_.*|fbclid|gclid|ref_src|ref|s|t|si|igsh)$", re.I)


def media_key(raw):
    """Normalizovaný klíč média; stejná logika jako mediaKey() v index.html."""
    try:
        u = urlsplit(raw.strip())
    except ValueError:
        return raw.strip().lower()
    host = re.sub(r"^(www|m|mobile)\.", "", (u.hostname or "").lower())
    if host == "twitter.com":
        host = "x.com"
    m = re.search(r"/status(?:es)?/(\d+)", u.path)
    if host == "x.com" and m:
        return "x:" + m.group(1)
    if host == "youtu.be":
        return "yt:" + u.path.lstrip("/").split("/")[0]
    q = parse_qsl(u.query)
    if host.endswith("youtube.com"):
        v = dict(q).get("v") or (re.search(r"/(?:shorts|embed|live)/([\w-]+)", u.path) or [None, None])[1]
        if v:
            return "yt:" + v
    q = [(k, v) for k, v in q if not TRACKING.match(k)]
    path = u.path.rstrip("/")
    path = re.sub(r"-\d{2,5}x\d{2,5}(?=\.(jpe?g|png|gif|webp)(\.webp)?$)", "", path, flags=re.I)
    path = re.sub(r"\.(jpe?g|png)\.webp$", r".\1", path, flags=re.I)
    return host + path + ("?" + urlencode(q) if q else "")


def duplicates(doc):
    """Vrátí (errors, warnings) pro duplicitní média a záznamy."""
    errors, warnings, seen_media, seen_items = [], [], {}, {}
    for u in doc.get("updates", []):
        local = set()
        for m in u.get("media", []) or []:
            k = media_key(m.get("url", ""))
            if k in local:
                errors.append(f"{u.get('id')}: stejné médium dvakrát v jednom záznamu ({m.get('url')})")
            local.add(k)
            if k in seen_media and seen_media[k] != u.get("id"):
                warnings.append(f"{u.get('id')}: médium už je u {seen_media[k]} ({m.get('url')}) – na webu se sloučí")
            seen_media.setdefault(k, u.get("id"))
        ik = (media_key(u.get("url", "")), u.get("title", "").strip().lower())
        if ik in seen_items:
            warnings.append(f"{u.get('id')}: stejný zdroj i titulek jako {seen_items[ik]} – možná duplicitní záznam")
        seen_items.setdefault(ik, u.get("id"))
    return errors, warnings


def validate(doc):
    errors, seen = [], set()
    for i, u in enumerate(doc.get("updates", [])):
        for k in REQUIRED:
            if not u.get(k):
                errors.append(f"updates[{i}] ({u.get('id')}): chybí '{k}'")
        if u.get("status") not in STATUSES:
            errors.append(f"updates[{i}] ({u.get('id')}): neplatný status '{u.get('status')}'")
        if u.get("id") in seen:
            errors.append(f"duplicitní id '{u.get('id')}'")
        seen.add(u.get("id"))
        for k in ("found_at", "published_at"):
            if u.get(k):
                try:
                    parse(u[k])
                except ValueError:
                    errors.append(f"updates[{i}] ({u.get('id')}): neplatné datum {k}='{u[k]}'")
        for m in u.get("media", []) or []:
            if m.get("thumb") and not str(m["thumb"]).startswith("https://"):
                errors.append(f"{u.get('id')}: thumb musí být https URL ({m['thumb']})")
            if m.get("thumb") and not m.get("credit"):
                errors.append(f"{u.get('id')}: médium s náhledem musí mít 'credit' (autor, nebo 'autor ve zdroji neuveden')")
        if not str(u.get("url", "")).startswith("http"):
            errors.append(f"updates[{i}] ({u.get('id')}): url musí začínat http")
    return errors


def main():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    site = cfg["site_url"].rstrip("/") + "/"
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    errors = validate(doc)
    dup_err, dup_warn = duplicates(doc)
    errors += dup_err
    for w in dup_warn:
        print("Upozornění: " + w, file=sys.stderr)
    if errors:
        print("Neplatná data:\n  " + "\n  ".join(errors), file=sys.stderr)
        sys.exit(1)

    updates = sorted(doc["updates"], key=lambda u: (u["found_at"], u["id"]), reverse=True)[:100]
    last = doc.get("meta", {}).get("last_check") or updates[0]["found_at"]

    items = []
    for u in updates:
        label = STATUSES[u["status"]]
        media = "".join(
            f'<br><a href="{escape(m["url"])}">{"Video" if m.get("type") == "video" else "Foto"}: {escape(m.get("caption", "odkaz"))}</a>'
            + (f' ({escape(m["credit"])}, via {escape(u["source"])})' if m.get("credit") else f' (via {escape(u["source"])})')
            for m in u.get("media", [])
        )
        desc = f"[{label}] {escape(u['text'])} (Zdroj: {escape(u['source'])}){media}"
        items.append(
            "    <item>\n"
            f"      <title>{escape('[' + label + '] ' + u['title'])}</title>\n"
            f"      <link>{escape(u['url'])}</link>\n"
            f"      <guid isPermaLink=\"false\">fz1073-{escape(u['id'])}</guid>\n"
            f"      <pubDate>{format_datetime(parse(u['found_at']))}</pubDate>\n"
            f"      <category>{escape(label)}</category>\n"
            f"      <description>{escape(desc)}</description>\n"
            "    </item>"
        )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        f"    <title>{escape(cfg.get('title', 'FZ1073 Incident Monitor'))}</title>\n"
        f"    <link>{escape(site)}</link>\n"
        f'    <atom:link href="{escape(site)}feed.xml" rel="self" type="application/rss+xml"/>\n'
        f"    <description>{escape(cfg.get('description', ''))}</description>\n"
        "    <language>cs</language>\n"
        f"    <lastBuildDate>{format_datetime(parse(last))}</lastBuildDate>\n"
        "    <ttl>60</ttl>\n"
        + "\n".join(items)
        + "\n  </channel>\n</rss>\n"
    )
    FEED.write_text(xml, encoding="utf-8")
    print(f"OK: {len(doc['updates'])} záznamů, feed.xml ({len(items)} položek)")


if __name__ == "__main__":
    main()
