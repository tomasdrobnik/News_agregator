#!/usr/bin/env python3
"""Validate data/updates.json (+ data/inbox.json) and regenerate feed.xml, feed-sk.xml, feed-en.xml (RSS 2.0).

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
INBOX = ROOT / "data" / "inbox.json"
FEEDS = {"cs": ROOT / "feed.xml", "sk": ROOT / "feed-sk.xml", "en": ROOT / "feed-en.xml"}
CONFIG = ROOT / "config.json"

STATUSES = {"official": "Oficiální", "data": "Data", "reported": "Média", "unconfirmed": "Neověřeno"}
LABELS = {
    "cs": STATUSES,
    "sk": {"official": "Oficiálne", "data": "Dáta", "reported": "Médiá", "unconfirmed": "Neoverené"},
    "en": {"official": "Official", "data": "Data", "reported": "Media", "unconfirmed": "Unconfirmed"},
}
WORDS = {
    "cs": {"video": "Video", "photo": "Foto", "link": "odkaz", "source": "Zdroj", "suffix": ""},
    "sk": {"video": "Video", "photo": "Foto", "link": "odkaz", "source": "Zdroj", "suffix": " (SK)"},
    "en": {"video": "Video", "photo": "Photo", "link": "link", "source": "Source", "suffix": " (EN)"},
}


def tr(obj, lang, key):
    """Text v daném jazyce; chybí-li překlad, vrátí češtinu."""
    if lang != "cs":
        v = ((obj.get("i18n") or {}).get(lang) or {}).get(key)
        if v:
            return v
    return obj.get(key, "")
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
                    dt = parse(u[k])
                except ValueError:
                    errors.append(f"updates[{i}] ({u.get('id')}): neplatné datum {k}='{u[k]}'")
                    continue
                if k == "found_at" and (dt - datetime.now(timezone.utc)).total_seconds() > 120:
                    errors.append(f"updates[{i}] ({u.get('id')}): found_at='{u[k]}' je v budoucnosti; použij `date -u +%Y-%m-%dT%H:%M:%SZ`")
        for m in u.get("media", []) or []:
            if m.get("thumb") and not str(m["thumb"]).startswith("https://"):
                errors.append(f"{u.get('id')}: thumb musí být https URL ({m['thumb']})")
            if m.get("thumb") and not m.get("credit"):
                errors.append(f"{u.get('id')}: médium s náhledem musí mít 'credit' (autor, nebo 'autor ve zdroji neuveden')")
        if not str(u.get("url", "")).startswith("http"):
            errors.append(f"updates[{i}] ({u.get('id')}): url musí začínat http")
    return errors


def validate_inbox(ids):
    """Vrátí (errors, warnings) pro data/inbox.json (tipy správce). Chybějící soubor = OK."""
    if not INBOX.exists():
        return [], []
    try:
        doc = json.loads(INBOX.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"inbox.json: neplatný JSON na řádku {e.lineno}, sloupci {e.colno} ({e.msg})"], []
    errors, warnings = [], []
    tips, processed = doc.get("tips", []), doc.get("processed", [])
    if not isinstance(tips, list) or not isinstance(processed, list):
        return ["inbox.json: 'tips' i 'processed' musí být seznamy [ ]"], []

    def norm(u):
        return str(u).strip().rstrip("/").lower()

    done = {}
    for i, p in enumerate(processed):
        if not isinstance(p, dict) or not str(p.get("url", "")).startswith("http"):
            errors.append(f"inbox processed[{i}]: chybí platné 'url'")
            continue
        try:
            parse(p.get("processed_at") or "")
        except ValueError:
            errors.append(f"inbox processed[{i}]: neplatné 'processed_at' ({p.get('processed_at')})")
        r = str(p.get("result", ""))
        if re.fullmatch(r"u\d{3}", r):
            if r not in ids:
                errors.append(f"inbox processed[{i}]: result '{r}' neodkazuje na existující záznam")
        elif not r.startswith("zamítnuto"):
            errors.append(f"inbox processed[{i}]: result musí být id záznamu (u0xx) nebo 'zamítnuto: důvod'")
        done[norm(p["url"])] = r

    seen = set()
    for i, t in enumerate(tips):
        url = t if isinstance(t, str) else t.get("url") if isinstance(t, dict) else None
        if not str(url or "").startswith("http"):
            errors.append(f"inbox tips[{i}]: tip musí být odkaz \"https://…\" nebo objekt s 'url'")
            continue
        if isinstance(t, dict) and t.get("added_at"):
            try:
                parse(t["added_at"])
            except ValueError:
                errors.append(f"inbox tips[{i}]: neplatné 'added_at' ({t['added_at']})")
        k = norm(url)
        if k in seen:
            warnings.append(f"inbox tips[{i}]: stejný odkaz je v tipech vícekrát ({url})")
        if k in done:
            warnings.append(f"inbox tips[{i}]: odkaz už byl zpracován ({done[k]}): {url}")
        seen.add(k)
    return errors, warnings


def main():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    site = cfg["site_url"].rstrip("/") + "/"
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    errors = validate(doc)
    dup_err, dup_warn = duplicates(doc)
    errors += dup_err
    inbox_err, inbox_warn = validate_inbox({u.get("id") for u in doc.get("updates", [])})
    errors += inbox_err
    for w in dup_warn + inbox_warn:
        print("Upozornění: " + w, file=sys.stderr)
    if errors:
        print("Neplatná data:\n  " + "\n  ".join(errors), file=sys.stderr)
        sys.exit(1)

    updates = sorted(doc["updates"], key=lambda u: (u["found_at"], u["id"]), reverse=True)[:100]
    last = doc.get("meta", {}).get("last_check") or updates[0]["found_at"]
    missing = [u["id"] for u in doc["updates"] if not all(((u.get("i18n") or {}).get(l) or {}).get("title") for l in ("sk", "en"))]
    if missing:
        print("Upozornění: chybí překlad SK/EN u " + ", ".join(missing), file=sys.stderr)

    for lang, path in FEEDS.items():
        labels, w = LABELS[lang], WORDS[lang]
        items = []
        for u in updates:
            label = labels[u["status"]]
            media = "".join(
                f'<br><a href="{escape(m["url"])}">{w["video"] if m.get("type") == "video" else w["photo"]}: {escape(tr(m, lang, "caption") or w["link"])}</a>'
                + (f' ({escape(m["credit"])}, via {escape(u["source"])})' if m.get("credit") else f' (via {escape(u["source"])})')
                for m in u.get("media", [])
            )
            desc = f"[{label}] {escape(tr(u, lang, 'text'))} ({w['source']}: {escape(u['source'])}){media}"
            items.append(
                "    <item>\n"
                f"      <title>{escape('[' + label + '] ' + tr(u, lang, 'title'))}</title>\n"
                f"      <link>{escape(u['url'])}</link>\n"
                f"      <guid isPermaLink=\"false\">fz1073-{escape(u['id'])}</guid>\n"
                f"      <pubDate>{format_datetime(parse(u['found_at']))}</pubDate>\n"
                f"      <category>{escape(label)}</category>\n"
                f"      <description>{escape(desc)}</description>\n"
                "    </item>"
            )
        ctitle = cfg.get("title", "FZ1073 Incident Monitor") + w["suffix"]
        cdesc = (cfg.get("description_i18n") or {}).get(lang) or cfg.get("description", "")
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
            "  <channel>\n"
            f"    <title>{escape(ctitle)}</title>\n"
            f"    <link>{escape(site)}?lang={lang}</link>\n"
            f'    <atom:link href="{escape(site)}{path.name}" rel="self" type="application/rss+xml"/>\n'
            f"    <description>{escape(cdesc)}</description>\n"
            f"    <language>{lang}</language>\n"
            f"    <lastBuildDate>{format_datetime(parse(last))}</lastBuildDate>\n"
            "    <ttl>60</ttl>\n"
            + "\n".join(items)
            + "\n  </channel>\n</rss>\n"
        )
        path.write_text(xml, encoding="utf-8")
    print(f"OK: {len(doc['updates'])} záznamů, feed.xml / feed-sk.xml / feed-en.xml ({len(updates)} položek)")


if __name__ == "__main__":
    main()
