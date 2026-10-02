# Photo/video search in the check routine

**ID:** P003
**Last updated:** 2026-10-02
**Status:** Active

---

## Current Understanding

- Hourly runs added text updates but no media (u014–u019) → `/check-fz1073` step 3 now runs a dedicated photo/video search every check (EN + AR + HE terms).
- The best finds are media embedded in articles from registered sites: `pic.twitter.com/…` links, YouTube embeds, caption lines ("Featured image:", "(Social media …)").
- YouTube channel owner: WebFetch `https://www.youtube.com/oembed?url=<URL>&format=json` → `author_name`.
- Accept only reputable outlets or their own channels. Rejected so far: Republic World (title swapped who stabbed whom), Cedar News (aggregator), TMZ (tabloid).
- Social/amateur footage = `unconfirmed`; credit the account that shared it plus "original author unknown"; warn in the entry text when footage is graphic.
- Stock photos and route maps (Airways, OMAAT lead images) → leave out or caption "ilustrační".

## Key Details

- First media entry from this approach: u020 (5 items: INN, Daily Telegraph YouTube, X video via OMAAT, The Media Line photo, ToI rudder photos).
- build_feed.py rejects a `found_at` in the future → always take the time from `date -u`.

## Related Topics

- See also: P001_avherald_asn_monitoring.md, P002_flightaware_source.md

## History

- 2026-09-30: Media search added to routine; u020 added
