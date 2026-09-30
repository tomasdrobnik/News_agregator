# FZ1073 Incident Monitor

Veřejný dashboard (GitHub Pages) sledující incident flydubai FZ1073 z 30. 9. 2026. Správce: Tomas (Safety / Compliance Manager, Elite Jet). Stránku sdílí s uživateli mimo organizaci; notifikace jsou přes RSS (`feed.xml`) a přímo na stránce.

## Incident (výchozí stav k 30. 9. 2026 12:25Z)
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
  - `official` – jen když byl text prohlášení dopravce/úřadu/vyšetřovacího orgánu **přímo přečten** na jeho oficiálním webu či účtu (WebFetch uspěl). Z výsledků vyhledávání nebo z citace v médiích nikdy `official`.
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
`data/updates.json`:
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
- Po každé změně spusť `python3 scripts/build_feed.py`. Validuje data a přegeneruje `feed.xml`, `feed-sk.xml`, `feed-en.xml` (upozorní na chybějící překlady). Při chybě necommituj.

## Zdroje
Seznam monitorovaných zdrojů je v **`data/sources.json`** (jediný zdroj pravdy). Každá kontrola projde všechny aktivní zdroje a hledá na webu další důvěryhodné zdroje; nové do registru přidá a od další kontroly je sleduje. Zdroje se nemažou, jen deaktivují (`active: false` + důvod). Každý web citovaný v záznamu (`url`) musí být v registru – web ho zobrazuje v záložce Zdroje.

- `access: "websearch"` = web blokuje automatické čtení (AvHerald, ASN) → jen WebSearch.
- Priorita: oficiální orgány (flydubai, GCAA UAE, GACA/AIB KSA, izraelské úřady) > agentury a renomovaná média > letecké weby > ostatní.

Nedostupné weby neobcházej (žádné curl, mirrory ani cache). Použij výsledky vyhledávání a v záznamu uveď, že obsah nebyl přímo čten.

## Rutina kontroly
Příkaz `/check-fz1073` (viz `.claude/commands/check-fz1073.md`).

## Struktura
- `index.html` – stránka se záložkami Aktualizace a Foto & video (agregace médií se sloučením duplicit a filtry typ/status/zdroj/nové); čte `data/updates.json` a každých 5 min kontroluje nové záznamy; stav „přečteno“ je v localStorage prohlížeče
- `data/sources.json` – registr monitorovaných zdrojů (rutina ho rozšiřuje)
- `feed.xml`, `feed-sk.xml`, `feed-en.xml` – generované RSS pro každý jazyk, needituj ručně
- `config.json` – `site_url` pro RSS (nastav na skutečnou adresu GitHub Pages)
- `scripts/build_feed.py` – validace + generování RSS

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
