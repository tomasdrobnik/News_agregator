# AvHerald + ASN monitoring routes

**ID:** P001
**Last updated:** 2026-09-30
**Status:** Active

---

## Current Understanding

- **AvHerald web / RSS:** robots.txt `User-agent: * Disallow: /` (only search-engine bots allowed) → the site's RSS feed is also off-limits. WebSearch only.
- **AvHerald on Bluesky (`avherald.com`, domain-verified handle):** posts every new/updated article headline + link. Readable through the public AT Protocol API with no login:
  `https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor=avherald.com&limit=20`
  robots.txt of public.api.bsky.app says crawling the public API is allowed (429 = back off). Works via WebFetch (tested 2026-09-30).
- Headlines change when AvHerald updates an article (same `article=` id, new post) → a good change detector.
- Only a headline is visible, not the article body → an entry based on it = `unconfirmed` ("headline in AvHerald's Bluesky feed; article not read directly").
- **ASN (aviation-safety.net):** Cloudflare 403 on everything incl. robots.txt and `/news/rss.xml`. WebSearch only.
- **ASN Bluesky `aviationsafety.bsky.social`:** 0 posts, unverified handle → useless. ASN is active on X (@AviationSafety) → tip route via inbox.json only.

## Key Details

- The handle `avherald.com` is domain-verified (DNS/well-known), so the account is authentic.
- Implemented 2026-09-30: registry source "The Aviation Herald – Bluesky" (`access: "curl"`, getAuthorFeed URL); `fetch_source.py` returns DIRECT READ OK (JSON body as text).
- /check-fz1073 step 3 filters posts by `article=5423fa17` / `#A6-FKF`; first entry from it = u014.

## History

- 2026-09-30: Initial documentation
- 2026-09-30: Bluesky feed wired into registry + routine; u014 added
