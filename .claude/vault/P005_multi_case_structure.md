# Multi-case structure (hub + case pages)

**ID:** P005
**Last updated:** 2026-11-02
**Status:** Active

---

## Current Understanding

- Site monitors several cases. `cases.json` is the case registry (paths, titles, RSS titles/descriptions, optional `social` queries).
- `index.html` = hub: lists cases, viewer follows cases (localStorage `monitor.follow`), sees unread counts, gets browser notifications only for followed cases.
- `case.html?c=<id>` = the former FZ1073 page, generalized (config from `cases.json`). No `?c` → fz1073.
- FZ1073 kept legacy paths on purpose (`data/`, root `feed*.xml`, `/check-fz1073`) so RSS subscribers and the cloud routine keep working. Old `/#aktualizace|media|zdroje` links redirect from hub to `case.html?c=fz1073`.
- New cases live in `cases/<id>/data/` + `cases/<id>/feed*.xml`, with own routine `.claude/commands/check-<id>.md`.
- First added case: N722BD (Learjet 60 crash, Palm Beach County, 1 Nov 2026). User typed "N2BD"; media give N722BD – user confirmed.

---

## Key Details

- localStorage keys: `<id>.read`, `<id>.mviewed` (fz1073 keys unchanged → users keep read state); language `monitor.lang` (falls back to old `fz1073.lang`).
- `build_feed.py` builds all cases (or `--case <id>`), validates `cases.json`; RSS guid = `<id>-u0xx` (FZ1073 guids unchanged); channel link → `case.html?c=<id>&lang=`.
- `fetch_source.py` allows hosts from the union of all cases' `sources.json`.
- `social_search.py --case <id>` (default fz1073); queries in `cases.json` → `social`. Case without `social` is skipped (N722BD has none yet).
- Ids `u001…` restart per case.
- N722BD direct-read OK (curl): FAA statements, FR24 blog, FlightAware, NBC, NBC 6, ABC, FlightGlobal (paywall: intro only), Simple Flying, IBTimes. Not readable: AP (403), Reuters (robots), NTSB newsroom/CAROL (JS), PBSO (robots timeout).
- FlightAware hides N722BD history at owner's request; owner LR60271 LLC.
- N722BD cloud routine `trig_01VG8oLALZJEYX5Ubb1LZVmf` ("N722BD source check"), every 3 h at :23 (`23 */3 * * *`), same env/model/tools as FZ1073, no MCP connectors (server auto-attached some – cleared). Reduce to daily after NTSB preliminary report.
- Decision 2026-11-02: no X/Reddit API search for N722BD (cost vs. value) – manual tips via inbox.json only.

---

## Gotchas

- When regex-editing the i18n table in case.html, the replaced prefix dropped `tabSources` – check keys against git HEAD after such edits.

---

## Related Topics

- See also: P004_routine_cadence_and_found_at.md (FZ1073 routine), P003_media_search_routine.md

---

## History

- 2026-11-02: Initial documentation (multi-case refactor, N722BD added)

---

**Lines: ~52 / 100 max**
