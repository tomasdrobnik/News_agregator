---
description: Zkontroluj zdroje k havárii Learjetu 60 N722BD, doplň nové záznamy, přegeneruj RSS a pushni
allowed-tools: WebSearch, WebFetch, Bash(python3 scripts/social_search.py:*), Read, Edit, Write, Bash(python3 scripts/build_feed.py:*), Bash(python3 scripts/fetch_source.py:*), Bash(git add:*), Bash(git checkout:*), Bash(git commit:*), Bash(git push:*), Bash(git pull:*), Bash(git status:*), Bash(date:*)
---

Proveď jednu kontrolu případu **N722BD** podle pravidel v CLAUDE.md (obecná pravidla + sekce případu N722BD).

Soubory případu (viz `cases.json`, id `n722bd`):
- data: `cases/n722bd/data/updates.json`, `cases/n722bd/data/sources.json`, `cases/n722bd/data/inbox.json`
- RSS: `cases/n722bd/feed.xml`, `feed-sk.xml`, `feed-en.xml` (generuje `build_feed.py`, needituj)

Data ostatních případů (`data/` = FZ1073) **neměň**.

1. `git pull --rebase` a zjisti aktuální čas: `date -u +%Y-%m-%dT%H:%M:%SZ`.
2. Načti `cases/n722bd/data/updates.json`. Zapamatuj si existující záznamy (url + obsah), ať nevznikají duplicity.
3. Zkontroluj zdroje:
   - Načti `cases/n722bd/data/sources.json` a zkontroluj **všechny** zdroje s `"active": true`:
     - `access: "curl"` → `python3 scripts/fetch_source.py "URL"` (URL z registru nebo konkrétní článek na stejném webu). `DIRECT READ OK` = přímo přečteno. `UNAVAILABLE` (exit 2) = nedostupné → dohledej přes WebSearch, v záznamu uveď „podle výsledků vyhledávání“, nic neobcházej. Opakuje-li se `UNAVAILABLE` u stejného zdroje, přepni ho na `"websearch"` a důvod dej do `note`.
     - `access: "webfetch"` → WebFetch; když selže, postupuj jako u `UNAVAILABLE`.
     - `access: "websearch"` → jen WebSearch (AvHerald, ASN, AP, Reuters, NTSB newsroom/CAROL, PBSO – viz `note` u zdroje).
     - `access: "tip"` (NTSB Newsroom na X) → jen tipy správce + WebSearch. Příspěvek NTSB na X známý jen z vyhledávání = `unconfirmed`; `official` až po přímém přečtení textu na ntsb.gov nebo jiném oficiálním webu.
     - **FAA** – stránka prohlášení `https://www.faa.gov/newsroom/statements/accident_incidents` (curl): hledej položku „Cresthaven“ / Learjet 60 a změny jejího textu, popř. odkaz na předběžný záznam FAA.
     - **NTSB** – priorita: briefing pro média (záznam na YouTube kanálu NTSB, tisková zpráva), předběžná zpráva (obvykle do ~30 dní) a záznam v CAROL (číslo šetření, např. ERA27FA…). WebFetch zkus na `https://www.ntsb.gov/news/press-releases/Pages/default.aspx` a `https://www.ntsb.gov/investigations/Pages/default.aspx`; jinak WebSearch.
     - **FlightAware** `https://www.flightaware.com/live/flight/N722BD/history` – historie je na žádost vlastníka skrytá; změnu (např. zveřejnění) zapiš jako `data`.
   - WebSearch (EN): `N722BD`, `Learjet 60 Palm Beach crash NTSB`, `Learjet Greenacres crash investigation`, `NTSB briefing West Palm Beach Learjet`, `NTSB preliminary report Learjet 60 N722BD`, `Learjet 60 crash victims identified Palm Beach`, `Aurora Aviation Learjet N722BD`, `avherald Learjet 60 West Palm Beach`, `aviation-safety.net N722BD`, `Bombardier statement Learjet 60 Florida`.
   - Přednost mají oficiální zdroje: NTSB, FAA, Palm Beach County Sheriff's Office / Fire Rescue, US DOT, Bahamas AAIA (pokud se zapojí). Pak agentury a renomovaná média (AP, Reuters, NBC, ABC, CBS, Palm Beach Post, WPTV, NBC 6), pak letecké weby (FlightGlobal, AIN, AvHerald, ASN, FR24).
   - **Hledání nových zdrojů:** najdi další důvěryhodné zdroje, které v registru ještě nejsou (např. Palm Beach Post, WPTV, Sun Sentinel, AIN, AvWeb, NTSB YouTube). Postup a pravidla stejné jako u FZ1073: nový zdroj zapiš do `cases/n722bd/data/sources.json` (`name`, `url`, `type` official|data|media|database|social, `access` – nejdřív `"curl"` a otestuj `fetch_source.py`; při `UNAVAILABLE` změň na `"websearch"` s důvodem v `note`, `added_at` = teď, `active: true`, `note`). Každý web citovaný v novém záznamu musí být v registru tohoto případu.
   - **Hledání fotek a videí (každá kontrola):** WebSearch `Learjet Palm Beach crash video`, `Greenacres jet crash dashcam`, `Learjet 60 crash Military Trail photos`, `NTSB Learjet 60 briefing video`, `N722BD photo`. Články ze registru přečti přímo a hledej vložená videa a fotky (YouTube, `pic.twitter.com`, popisky „Photo:“, „Credit:“). U YouTube zjisti autora přes `https://www.youtube.com/oembed?url=<URL>&format=json` (WebFetch). Přidávej jen média renomovaných médií nebo oficiálních kanálů (NTSB, PBSO, PBC Fire Rescue). Amatérské záběry a sociální sítě = `unconfirmed`, v `credit` účet, který je sdílel. Stock fotky letadla označ „ilustrační“, nebo nepřidávej. Záběry dopadu (dashcam) označ v textu „některá videa mohou být drastická“.
   - **Sociální sítě přes API:** `python3 scripts/social_search.py --case n722bd`. Dokud v `cases.json` není pro případ `social`, skript se přeskočí – to je v pořádku.
   - **Tipy správce:** `cases/n722bd/data/inbox.json` – zpracuj stejně jako u FZ1073 (příspěvek sám o sobě = `unconfirmed`, `source` = autor příspěvku, zpracovaný tip přesuň do `processed`).
4. U fotek a videí nejdřív ověř duplicity (twitter/x, youtu.be/youtube, zmenšeniny, sledovací parametry). U nového média zjisti `og:image` / autora a vyplň `thumb` a `credit` podle CLAUDE.md.
5. Za každou **skutečně novou nebo změněnou** informaci přidej záznam do `updates` (nové `id` – pokračuj od nejvyššího `u0xx` v tomto souboru, `found_at` = teď, status podle CLAUDE.md, `i18n` SK + EN). Při pochybnosti `unconfirmed`. `official`/`data` jen při přímém přečtení zdroje. Jména obětí ani pilotů nezveřejňuj, i kdyby je média uvedla.
6. Aktualizuj `meta`: `last_check` = teď, `next_check` = teď + 1 h, `new_count` = počet přidaných.
7. `python3 scripts/build_feed.py --case n722bd`. Pokud selže, oprav data a spusť znovu.
8. Commit a push (jen soubory tohoto případu):
   - nové záznamy: `git add cases/n722bd && git commit -m "N722BD: +N aktualizací (HH:MMZ)"` (pokud přibyly zdroje, přidej `, +M zdrojů`)
   - jen nové zdroje: commitni jen `cases/n722bd/data/sources.json` (`N722BD: +M zdrojů (HH:MMZ)`), ostatní vrať
   - jen zpracované tipy: commitni jen `cases/n722bd/data/inbox.json` (+ `social_state.json`, existuje-li) – `N722BD: tipy zpracovány (HH:MMZ)`
   - nic nového: **necommituj a nepushuj** (`git checkout -- cases/n722bd`).
9. Na závěr stručně česky vypiš nové záznamy (status, co se změnilo, zdroj). Pokud nic nového, napiš jen „Beze změn“.
10. Pokud vyšla předběžná/finální zpráva NTSB nebo 72 h nepřibylo nic nového, upozorni na to a navrhni snížit frekvenci kontrol.
