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
- Veškerý text pro uživatele **česky**.
- Buď kritický. Každý záznam má status:
  - `official` – prohlášení dopravce, úřadu, vyšetřovacího orgánu
  - `data` – primární data (ADS-B/FR24, METAR, NOTAM)
  - `reported` – média, i když citují nejmenované představitele
  - `unconfirmed` – jednotlivý zdroj, spekulace, vzájemně rozporné údaje
- Status zvyšuj jen tehdy, když ho potvrdí oficiální zdroj. Mediální tvrzení nikdy neprezentuj jako fakt. Rozpory mezi zdroji výslovně uveď.
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
- Po každé změně spusť `python3 scripts/build_feed.py`. Validuje data a přegeneruje `feed.xml`. Při chybě necommituj.

## Zdroje
Seznam monitorovaných zdrojů je v **`data/sources.json`** (jediný zdroj pravdy). Každá kontrola projde všechny aktivní zdroje a hledá na webu další důvěryhodné zdroje; nové do registru přidá a od další kontroly je sleduje. Zdroje se nemažou, jen deaktivují (`active: false` + důvod).

- `access: "websearch"` = web blokuje automatické čtení (AvHerald, ASN) → jen WebSearch.
- Priorita: oficiální orgány (flydubai, GCAA UAE, GACA/AIB KSA, izraelské úřady) > agentury a renomovaná média > letecké weby > ostatní.

Nedostupné weby neobcházej (žádné curl, mirrory ani cache). Použij výsledky vyhledávání a v záznamu uveď, že obsah nebyl přímo čten.

## Rutina kontroly
Příkaz `/check-fz1073` (viz `.claude/commands/check-fz1073.md`).

## Struktura
- `index.html` – stránka se záložkami Aktualizace a Foto & video (agregace médií se sloučením duplicit a filtry typ/status/zdroj/nové); čte `data/updates.json` a každých 5 min kontroluje nové záznamy; stav „přečteno“ je v localStorage prohlížeče
- `data/sources.json` – registr monitorovaných zdrojů (rutina ho rozšiřuje)
- `feed.xml` – generovaný RSS, needituj ručně
- `config.json` – `site_url` pro RSS (nastav na skutečnou adresu GitHub Pages)
- `scripts/build_feed.py` – validace + generování RSS
