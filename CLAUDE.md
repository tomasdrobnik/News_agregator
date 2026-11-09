# Incident Monitor (více případů)

Veřejný dashboard (GitHub Pages) sledující letecké incidenty a nehody. Správce: Tomas (Safety / Compliance Manager, Elite Jet). Stránku sdílí s uživateli mimo organizaci; notifikace jsou přes RSS (každý případ má vlastní feed) a přímo na stránce.

## Případy
- Registr případů je **`cases.json`** (jediný zdroj pravdy): `id`, `status` (`active`/`closed`), `date`, `data_dir`, `feed_dir`, `command`, `title`, `sub` + `i18n`, `feed_title`, `description` + `description_i18n`, volitelně `social` (dotazy pro `social_search.py`).
- `index.html` = rozcestník: seznam případů, uživatel si vybere, které sleduje (localStorage `monitor.follow`), vidí počet nových zpráv a dostává upozornění jen u sledovaných. `case.html?c=<id>` = stránka případu (záložky Aktualizace / Foto & video / Zdroje).
- Každý případ má vlastní `updates.json`, `sources.json`, `inbox.json` v `data_dir` a RSS v `feed_dir`. Pravidla obsahu, statusy a pravidla zdrojů níže platí **pro všechny případy**. Id záznamů (`u001`…) jsou číslována zvlášť v každém případě.
- **FZ1073** (`fz1073`): kvůli existujícím odběratelům RSS a cloudové rutině zůstává v původních cestách – data `data/`, RSS `feed.xml` v kořeni, rutina `/check-fz1073`. Staré odkazy `/#aktualizace` apod. přesměruje rozcestník na `case.html?c=fz1073`.
- **N722BD** (`n722bd`): data `cases/n722bd/data/`, RSS `cases/n722bd/feed*.xml`, rutina `/check-n722bd`.
- **Nový případ:** přidej položku do `cases.json`, založ `cases/<id>/data/{updates,sources,inbox}.json`, sekci případu do tohoto souboru a rutinu `.claude/commands/check-<id>.md` (podle `check-n722bd.md`), pak `python3 scripts/build_feed.py`.
- Rutina případu mění jen soubory svého případu.

## Případ N722BD (výchozí stav k 2. 11. 2026 10:05Z)
- Learjet 60 **N722BD** (r. v. 2004), let Austin-Bergstrom (AUS) → North Eleuthera (ELH, Bahamy), 1. 11. 2026. Havárie kolem 12:50 LT (17:49Z) v obytné oblasti Palm Beach County (Greenacres / Cresthaven), Florida. Na palubě 9 osob, všechny zahynuly (ministr dopravy podle médií).
- **Oficiálně (FAA, přímo přečteno):** havárie u Cresthaven, 9 osob, šetření vede NTSB, FAA se podílí.
- **Data (FR24 ADS-B):** v 17:48Z krátké stoupání, pak strmý pravotočivý sestup; poslední údaj 8 750 ft v 17:49:22Z, > 32 000 ft/min. Posádka podle záznamu ATC hlásila námrazu, mírnou turbulenci, srážky a žádala FL370; pak mayday a overspeed.
- **Neověřeno / rozpory:** místo (FAA „Cresthaven“ / NTSB „Lake Worth Beach“ / šerif Military Trail); provozovatel a režim letu (Part 91 vs. charter Part 135 – zmiňována Aurora Aviation); sériové číslo (60-271 vs. 60-186). Vlastník v registru: LR60271 LLC (Wilmington, DE).
- Otevřené otázky: příčina (námraza / turbulence / overspeed / jiné), provozovatel, kvalifikace posádky, předběžná zpráva NTSB.
- Jména obětí a pilotů nezveřejňuj (platí obecné pravidlo níže).

## Případ FZ1073 – incident (výchozí stav k 30. 9. 2026 12:25Z)
- Let FZ1073 DXB→TLV, B737-8 **A6-FKF**, vzlet 03:05Z, FL340.
- 05:21Z výškové výkyvy, 05:22Z pokles >14 000 ft za <30 s (FR24); 05:31Z squawk 7700, 05:38Z 7500, poté zpět 7700; přistání Tabuk (TUU) ~06:45Z.
- **Oficiálně (flydubai):** incident během letu, bezpečné přistání v TUU, všichni cestující v pořádku. Příčinu neuvádí.
- **Média / izraelští představitelé (neověřeno UAE/KSA):** F/O měl napadnout kapitána; zásah záložního pilota a cestujících; Izrael hodnotí jako pokus o teroristický čin.
- **Neověřeno:** národnost F/O (Omán), poškození směrovky (JPost), počet osob na palubě (174 / ~150 / ~180).
- Rozpor: profil sestupu (FR24: >14 000 ft za <30 s vs. jiné zdroje 17 000 ft za ~2 min).
- Otevřené otázky: kdo nastavil 7500 a proč; kdo vede šetření (GCAA UAE / GACA-AIB KSA, Annex 13 vs. bezpečnostní vyšetřování); režim dvou osob v kokpitu; přítomnost záložního pilota.

## Pravidla obsahu (závazná)
- Stránka je trojjazyčná (CZ / SK / EN, přepínač v záhlaví). Hlavní `title`, `text` a `caption` jsou **česky**. Každý nový záznam musí mít i překlad v `i18n`: `{"sk": {"title", "text"}, "en": {"title", "text"}}`, u médií `i18n: {"sk": {"caption"}, "en": {"caption"}}`. Překlad je věrný české verzi (stejný status i míra nejistoty). Chybí-li překlad, web ukáže češtinu s označením CZ.
- Monitoring informace **jen agreguje** – správce je ručně neověřuje. Status proto musí být konzervativní. **Při jakékoli pochybnosti = `unconfirmed`.**
- Statusy:
  - `official` – jen když byl text prohlášení dopravce/úřadu/vyšetřovacího orgánu **přímo přečten** na jeho oficiálním webu či účtu (přímé čtení uspělo – WebFetch nebo `scripts/fetch_source.py`, viz Zdroje). Z výsledků vyhledávání nebo z citace v médiích nikdy `official`.
  - `data` – primární data (ADS-B/FR24, METAR, NOTAM) **přímo přečtená** ze zdroje.
  - `reported` – článek renomovaného média/agentury, jehož obsah je jasný (přímo přečten, nebo shodně ve výsledcích vyhledávání u ≥ 2 renomovaných médií). Tvrzení médií nikdy nepodávej jako fakt.
  - `unconfirmed` – vše ostatní: jen úryvky z vyhledávání, jediný zdroj, agregátory, sociální sítě, spekulace, rozporné údaje, nedostupná stránka.
- Status nikdy neodhaduj směrem nahoru. Zvýšit ho lze až novým záznamem, když se objeví přímo přečtený oficiální zdroj. Rozpory mezi zdroji výslovně uveď. Pokud stránka nebyla přímo přečtena, uveď to v textu („podle výsledků vyhledávání“).
- Text záznamu: 1–3 věty **vlastními slovy**, bez delších citací (max. jedna krátká citace do 15 slov na zdroj).
- Fotky a videa **nikdy nestahuj do repa**. Stránka zobrazuje náhled načtený přímo ze zdroje.
- `thumb` = náhledový obrázek, který zdroj sám zveřejňuje: `og:image` / `twitter:image` stránky, přímá URL obrázku, nebo pro YouTube nic (web si náhled odvodí sám). Nic nevymýšlej. Když zdroj náhled nemá, `thumb` vynech.
- `credit` = autor/agentura dle popisku ve zdroji (např. „Markus Mainka / Shutterstock.com“). Pokud zdroj autora neuvádí, napiš „autor ve zdroji neuveden“. Médium s `thumb` musí mít `credit`.
- Ilustrační (ne z incidentu) snímky označ v `caption` slovem „ilustrační“.
- Žádné osobní údaje osob na palubě kromě toho, co zveřejnil sám zdroj a je to podstatné. Jména pilotů nezveřejňuj.

## Data
`<data_dir>/updates.json` (FZ1073: `data/updates.json`, N722BD: `cases/n722bd/data/updates.json`):
```json
{
  "meta": {"incident": "...", "last_check": "ISO UTC", "next_check": "ISO UTC", "new_count": 0},
  "updates": [
    {"id": "u010", "found_at": "ISO UTC", "published_at": "ISO UTC | null",
     "source": "název", "url": "https://...", "title": "…", "text": "…",
     "status": "official|data|reported|unconfirmed",
     "media": [{"type": "photo|video", "caption": "…", "url": "https://...",
                "thumb": "https://... (volitelné)", "credit": "autor / agentura"}]}
  ]
}
```
- `id` je `u` + trojmístné číslo, pokračuj od nejvyššího existujícího. Existující `id` nikdy neměň (stránka podle něj eviduje stav „přečteno“ u uživatelů).
- Opravu staršího záznamu zapiš jako **nový** záznam, který na původní odkazuje. Starý záznam nepřepisuj.
- Média: stejné foto/video nepřidávej opakovaně. `build_feed.py` porovnává normalizované URL (twitter↔x, youtu.be↔youtube, zmenšeniny obrázků, sledovací parametry). Duplicita v rámci jednoho záznamu je chyba, napříč záznamy jen upozornění (web je sloučí do jedné karty).
- Po každé změně spusť `python3 scripts/build_feed.py` (všechny případy) nebo `--case <id>`. Validuje `cases.json` a data a přegeneruje `feed.xml`, `feed-sk.xml`, `feed-en.xml` každého případu (upozorní na chybějící překlady). Při chybě necommituj.

## Zdroje
Seznam monitorovaných zdrojů je v **`<data_dir>/sources.json`** každého případu (jediný zdroj pravdy pro daný případ; FZ1073: `data/sources.json`). Každá kontrola projde všechny aktivní zdroje a hledá na webu další důvěryhodné zdroje; nové do registru přidá a od další kontroly je sleduje. Zdroje se nemažou, jen deaktivují (`active: false` + důvod). Každý web citovaný v záznamu (`url`) musí být v registru – web ho zobrazuje v záložce Zdroje.

- `access` určuje způsob čtení:
  - `"curl"` = web je dostupný a povoluje automatické čtení → přímé čtení jen přes `python3 scripts/fetch_source.py URL` (read-only GET).
  - `"webfetch"` = přímé čtení přes WebFetch.
  - `"tip"` = sociální síť, jen tipy správce přes `data/inbox.json` (viz níže).
  - `"api"` = sociální síť hledaná automaticky přes oficiální API (`scripts/social_search.py`) + tipy správce.
  - `"websearch"` = web automatické čtení zakazuje nebo blokuje → jen WebSearch. Týká se: AvHerald (`robots.txt`: `Disallow: /` pro všechny boty, i RSS), ASN (Cloudflare challenge, i RSS; Bluesky účet ASN je neaktivní), flydubai.com (Akamai 403).
  - AvHerald má navíc oficiální Bluesky účet `@avherald.com` čitelný přes veřejné API (`public.api.bsky.app`, `access: "curl"`). Jsou v něm jen titulky → záznam z nich je vždy `unconfirmed`.
- Přímé čtení (`curl` i `webfetch`) se počítá jako „přímo přečteno“ pro statusy `official` / `data` / `reported`.
- Pravidla pro `fetch_source.py` (skript je sám vynucuje): jen host aktivního zdroje s `access: "curl"` v registru kteréhokoli případu z `cases.json`; `robots.txt` musí čtení povolit; jeden GET s poctivým User-Agentem `FZ1073-monitor/1.0`; žádné opakování s jiným UA, cookies ani obcházení ochrany. Návratový kód 2 / `UNAVAILABLE` = zdroj nedostupný → použij WebSearch a v záznamu uveď, že obsah nebyl přímo čten. Curl ani jiné nástroje mimo tento skript na zdroje nepoužívej.
- Zdroj převeď na `"curl"` jen po úspěšném testu skriptem; když skript opakovaně vrací `UNAVAILABLE` (403, challenge, robots), vrať ho na `"websearch"` a důvod zapiš do `note`.
- Priorita: oficiální orgány (flydubai, GCAA UAE, GACA/AIB KSA, izraelské úřady) > agentury a renomovaná média > letecké weby > ostatní.

**Tipy správce (sociální sítě):** X, Instagram, Facebook a Reddit se automaticky nemonitorují (vyžadují přihlášení; fóra a anonymní účty nejsou zdroj pro registr). Správce vkládá odkazy na příspěvky jiných lidí do `inbox.json` daného případu (`tips`); rutina je zpracuje a přesune do `processed` (`result` = id záznamu nebo „zamítnuto: důvod“). Tip může být samotný odkaz nebo objekt s `url`; formát kontroluje `build_feed.py`. Platformy jsou v registru jako `type: "social"`, `access: "tip"`. Příspěvek sám o sobě = `unconfirmed`; `source` je autor příspěvku, ne správce. Přístupové údaje ke svým účtům správce nikdy nesdílí.

**Automatické hledání přes API (X, Reddit):** `scripts/social_search.py [--case <id>]` (výchozí `fz1073`; dotazy v `cases.json` → `social`, bez nich se případ přeskočí) hledá nové příspěvky přes oficiální API a řadí je do `inbox.json` jako tipy (`via: "x-api" | "reddit-api"`); zpracují se stejně jako ostatní tipy (sám o sobě = `unconfirmed`). Klíče jsou **jen** v proměnných prostředí cloudového prostředí (`X_BEARER_TOKEN`; `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`), nikdy v repu ani v chatu. X je placené per-use (0,005 USD za přečtený příspěvek, docs.x.com, 30. 9. 2026) – skript bere max. 10 příspěvků na běh. Text příspěvků se do repa neukládá. Facebook a Instagram API pro hledání veřejných příspěvků nenabízí → jen ruční tipy. Stav kurzoru: `<data_dir>/social_state.json`.

Nedostupné nebo zakázané weby neobcházej (žádné mirrory, cache, změna User-Agenta ani obcházení ochrany proti botům). Použij výsledky vyhledávání a v záznamu uveď, že obsah nebyl přímo čten.

## Komunikace se správcem
- Když je požadavek nejasný nebo chybí údaj potřebný pro správnou/bezpečnou odpověď, ptej se **interaktivně** (nástroj AskUserQuestion s volbami) a **vždy jen jednu otázku najednou**. Další otázku polož až po odpovědi. Otázky nevypisuj hromadně v textu.
- Doporučenou volbu dej první a označ „(Recommended)“.
- Fakta uváděj se zdrojem; co není ověřeno, výslovně označ jako názor.

## Rutina kontroly
Jeden příkaz na případ: `/check-fz1073`, `/check-n722bd` (viz `.claude/commands/`).

## Struktura
- `cases.json` – registr případů
- `index.html` – rozcestník případů (výběr sledovaných, počty nových, upozornění)
- `case.html?c=<id>` – stránka případu se záložkami Aktualizace, Foto & video (agregace médií se sloučením duplicit a filtry typ/status/zdroj/nové) a Zdroje; každých 5 min kontroluje nové záznamy; stav „přečteno“ je v localStorage prohlížeče (`<id>.read`, `<id>.mviewed`)
- `<data_dir>/updates.json`, `sources.json`, `inbox.json` – data, registr zdrojů a schránka tipů případu (FZ1073 `data/`, N722BD `cases/n722bd/data/`)
- `feed.xml`, `feed-sk.xml`, `feed-en.xml` v `feed_dir` případu – generované RSS pro každý jazyk, needituj ručně
- `config.json` – `site_url` pro RSS (nastav na skutečnou adresu GitHub Pages)
- `scripts/social_search.py` – hledání na X a Redditu přes oficiální API → tipy do `inbox.json`
- `scripts/build_feed.py` – validace (`cases.json`, `updates.json` + `inbox.json`) + generování RSS všech případů (`--case <id>` jen jeden)
- `scripts/fetch_source.py` – přímé read-only čtení zdrojů s `access: "curl"` (kontrola registru, robots.txt, bot challenge; vypíše og:/meta tagy a text)

---

## 🚨 CONTEXTVAULT - MANDATORY (DO NOT SKIP!) 🚨

**STOP. READ THIS. FOLLOW IT.**

### ⚡ AFTER EVERY TASK - DOCUMENT IMMEDIATELY ⚡

┌─────────────────────────────────────────────────────────────────┐
│  COMPLETED A TASK? → DOCUMENT IT NOW!                           │
│                                                                 │
│  ✅ Fixed a bug?        → /ctx-error or /ctx-doc                │
│  ✅ Made a decision?    → /ctx-decision                         │
│  ✅ Learned something?  → /ctx-doc                              │
│  ✅ Found useful code?  → /ctx-doc type=snippet                 │
│  ✅ Explored codebase?  → /ctx-doc type=intel                   │
│  ✅ Ending session?     → /ctx-handoff                          │
│                                                                 │
│  💭 Not every edit needs documenting                             │
│  💭 Document at milestones, not mid-edit                         │
│  💭 Skip if nothing meaningful was learned                       │
└─────────────────────────────────────────────────────────────────┘

### SESSION START (AUTOMATIC):
1. Read `./.claude/vault/index.md` immediately
2. Review what's already documented
3. Use that knowledge in your work

### WHEN TO DOCUMENT:
- Feature complete → /ctx-doc
- Bug fix solved → /ctx-error
- Architecture decision → /ctx-decision
- Session ending → /ctx-handoff
- NOT: trivial edits, version bumps, mid-refactor

### RULES:
- Project docs → `./.claude/vault/` with P### prefix
- ALWAYS update index after doc changes
- Search before creating (no duplicates)

### COMMANDS:
`/ctx-doc` `/ctx-error` `/ctx-decision` `/ctx-handoff` `/ctx-search` `/ctx-read` `/ctx-bootstrap` `/ctx-plan`

## Git: confirm, then commit AND push

When a task/topic is coded and no open questions remain, give a brief summary and ask me to confirm via `AskUserQuestion` ("Commit and push?"). After I confirm, commit and push in the same step. Never leave a commit unpushed or finished work uncommitted. Do not commit/push before I confirm.

## Idle session: offer /ctx-handoff

To avoid losing prompt-cache data and wasting tokens: when I have been inactive for a while (a turn ends with work paused, or my next message arrives after a long gap, roughly 5+ minutes), ask via `AskUserQuestion` whether to run `/ctx-handoff` now. Do not run it without my answer.
