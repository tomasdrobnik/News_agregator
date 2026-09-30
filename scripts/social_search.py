#!/usr/bin/env python3
"""Search X and Reddit for new FZ1073 posts via their official APIs and queue them as tips.

Usage: python3 scripts/social_search.py [--dry-run]

Keys come only from environment variables (cloud environment settings, never the repo):
  X_BEARER_TOKEN                                  – X API v2, app-only (pay-per-use, see X_MAX_RESULTS)
  REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET,         – Reddit "script" app approved by Reddit,
  REDDIT_USERNAME                                    app-only OAuth (client_credentials)
A platform without keys is skipped.

New posts are appended to data/inbox.json "tips" as {"url", "added_at", "via"}; the post text is
printed to stdout only (not stored in the public repo) so the check routine can assess it.
The routine then processes them like any other tip (CLAUDE.md: a post on its own = unconfirmed).
Cursor state (X since_id) is kept in data/social_state.json.

Exit codes: 0 = OK (also when all platforms are skipped), 1 = API/network error on some platform.
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "data" / "inbox.json"
STATE = ROOT / "data" / "social_state.json"
TIMEOUT = 25

# One search request per platform per run. X bills each returned post ($0.005 per read, docs.x.com,
# checked 2026-09-30): 10 posts x hourly checks = max ~7 200 reads ≈ 36 USD / month.
X_MAX_RESULTS = 10  # API minimum is 10
X_QUERY = '(FZ1073 OR "A6-FKF" OR (flydubai (Tabuk OR hijack OR 7500 OR "first officer"))) -is:retweet'
REDDIT_QUERY = 'FZ1073 OR "A6-FKF" OR (flydubai AND (Tabuk OR hijack OR 7500))'
REDDIT_LIMIT = 25


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def norm(u):
    return str(u).strip().rstrip("/").lower().replace("://twitter.com/", "://x.com/").replace("://www.reddit.com/", "://reddit.com/")


def http_json(url, headers, data=None):
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


def search_x(state):
    token = os.environ.get("X_BEARER_TOKEN")
    if not token:
        return None
    params = {"query": X_QUERY, "max_results": X_MAX_RESULTS, "tweet.fields": "created_at,lang",
              "expansions": "author_id", "user.fields": "username"}
    if state.get("x_since_id"):
        params["since_id"] = state["x_since_id"]
    doc = http_json("https://api.x.com/2/tweets/search/recent?" + urlencode(params),
                    {"Authorization": f"Bearer {token}", "User-Agent": "FZ1073-monitor/1.0"})
    users = {u["id"]: u["username"] for u in doc.get("includes", {}).get("users", [])}
    if doc.get("meta", {}).get("newest_id"):
        state["x_since_id"] = doc["meta"]["newest_id"]
    posts = []
    for t in doc.get("data", []):
        user = users.get(t.get("author_id"), "i")
        posts.append({"url": f"https://x.com/{user}/status/{t['id']}", "author": "@" + user,
                      "created_at": t.get("created_at"), "text": t.get("text", ""), "via": "x-api"})
    return posts


def search_reddit(state):
    cid, secret, user = (os.environ.get(k) for k in ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME"))
    if not (cid and secret and user):
        return None
    ua = f"python:fz1073-monitor:1.0 (by /u/{user})"
    basic = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    tok = http_json("https://www.reddit.com/api/v1/access_token",
                    {"Authorization": f"Basic {basic}", "User-Agent": ua,
                     "Content-Type": "application/x-www-form-urlencoded"},
                    data=b"grant_type=client_credentials")["access_token"]
    params = {"q": REDDIT_QUERY, "sort": "new", "t": "week", "limit": REDDIT_LIMIT, "type": "link", "raw_json": 1}
    doc = http_json("https://oauth.reddit.com/search?" + urlencode(params),
                    {"Authorization": f"Bearer {tok}", "User-Agent": ua})
    posts = []
    for c in doc.get("data", {}).get("children", []):
        d = c.get("data", {})
        created = datetime.fromtimestamp(d.get("created_utc", 0), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        posts.append({"url": "https://www.reddit.com" + d.get("permalink", ""), "author": "u/" + str(d.get("author")),
                      "created_at": created, "text": (d.get("title", "") + "\n" + d.get("selftext", ""))[:1500],
                      "link": d.get("url_overridden_by_dest") or "", "subreddit": d.get("subreddit_name_prefixed", ""),
                      "via": "reddit-api"})
    return posts


def main():
    dry = "--dry-run" in sys.argv
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
    before = dict(state)
    inbox = json.loads(INBOX.read_text(encoding="utf-8"))
    known = {norm(t if isinstance(t, str) else t.get("url", "")) for t in inbox.get("tips", [])}
    known |= {norm(p.get("url", "")) for p in inbox.get("processed", [])}

    failed, added = False, []
    for name, fn in (("X", search_x), ("Reddit", search_reddit)):
        try:
            posts = fn(state)
        except (urllib.error.URLError, KeyError, ValueError) as e:
            print(f"{name}: CHYBA {e} – platforma v tomto běhu přeskočena")
            failed = True
            continue
        if posts is None:
            print(f"{name}: přeskočeno (chybí klíče v proměnných prostředí)")
            continue
        new = [p for p in posts if norm(p["url"]) not in known]
        print(f"{name}: {len(posts)} nalezeno, {len(new)} nových")
        for p in new:
            known.add(norm(p["url"]))
            added.append(p)

    for p in added:
        print("\n---", p["via"], p["url"])
        print("autor:", p["author"], "| vytvořeno:", p["created_at"], ("| " + p["subreddit"]) if p.get("subreddit") else "")
        if p.get("link"):
            print("odkaz v příspěvku:", p["link"])
        print(p["text"])

    if added and not dry:
        ts = now()
        inbox.setdefault("tips", []).extend({"url": p["url"], "added_at": ts, "via": p["via"]} for p in added)
        INBOX.write_text(json.dumps(inbox, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not dry and state != before:
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nPřidáno do data/inbox.json: {0 if dry else len(added)} tipů" + (" (dry-run)" if dry else ""))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
