# FlightAware as a source

**ID:** P002
**Last updated:** 2026-10-02
**Status:** Active

---

## Current Understanding

- Registry entry "FlightAware" (`https://www.flightaware.com`, `type: data`, `access: curl`). fetch_source.py matches by host, so every flightaware.com URL is readable; robots.txt allows it (test 2026-10-02 11:07Z).
- **Flight history** `https://www.flightaware.com/live/flight/FDB1073/history` (ICAO callsign FDB, not FZ) = primary data: cancellations, a resumed service, aircraft type → status `data`.
- **Squawks** `/squawks/browse/general/7_days/popular` = links submitted by FlightAware users. Use only to discover articles; cite the linked article, never the squawk or user comments.
- As of 2026-10-02: FZ1073 cancelled 1 and 2 Oct, 3 Oct scheduled. Not recorded yet; the user chose to leave it to the hourly routine.

## Key Details

- Routine step lives in `.claude/commands/check-fz1073.md` step 3 ("FlightAware").
- og:image on FlightAware pages is a generic default image → never use it as `thumb`.

## Related Topics

- See also: P001_avherald_asn_monitoring.md, P003_media_search_routine.md

## History

- 2026-10-02: Added as "FlightAware Squawks", then widened to the whole site
