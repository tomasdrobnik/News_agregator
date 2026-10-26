# Routine cadence and found_at timestamps

**ID:** P002
**Last updated:** 2026-10-26
**Status:** Active

---

## Current Understanding

- Cloud routine `trig_01EWopbr79qU7HUyTTEdbxEa` ("FZ1073 daily source check") runs daily at 18:09Z (`9 18 * * *`). It was hourly (`9 * * * *`) until 2026-10-26.
- Update rate decayed: 25 entries on 30 Sep, 44 in the first 2 days, ~1.2/day for 13-23 Oct (gaps 1-4 days). Daily is enough; switch back to ~6h if a final report or investigation announcement appears.
- The routine prompt has a binding step 0: run `date -u` first and use the real value for `found_at`, `last_check`, commit message and notification.
- `scripts/build_feed.py` rejects a `found_at` more than 2 min in the future.

---

## Key Details

- Routine settings are changed with RemoteTrigger `update` (partial body works: `cron_expression`, `name`; the prompt needs the full `job_config.ccr`).
- Run logs: RemoteTrigger `list_runs` then `get_run_log`.
- `PushNotification` only reports "requested", never "delivered".

---

## Gotchas

- 2026-09-30 14:10Z run hardcoded `found_at` 14:20Z (never called `date -u`), so u015/u016 are stamped ~9 min early. Old entries are not rewritten (CLAUDE.md rule).
- The routine once ended on a detached HEAD; the prompt now says to `git checkout main` first.
- Commit message HH:MMZ can still be rounded ~30 s ahead of the real time; `found_at` itself is correct.

---

## Related Topics

- See also: P001_avherald_asn_monitoring.md

---

## History

- 2026-10-26: Hourly to daily 18:09Z, renamed to "daily"; prompt text still says "hourly check".
- 2026-09-30: found_at bug found and fixed (prompt step 0 + build_feed.py guard, commit 7bb565a).

---

**Lines: ~42 / 100 max**
