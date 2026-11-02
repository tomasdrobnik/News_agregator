# Incident Monitor

Statický dashboard pro GitHub Pages sledující letecké incidenty a nehody. Úvodní stránka je rozcestník případů – uživatel si vybere, které chce sledovat (u nich vidí počet nových zpráv a dostává upozornění). Každý případ má vlastní stránku (`case.html?c=<id>`), data a RSS.

Aktuální případy (registr `cases.json`):
- **N722BD** – havárie Learjetu 60 v Palm Beach County, Florida (1. 11. 2026) – `cases/n722bd/`, rutina `/check-n722bd`
- **FZ1073** – incident flydubai DXB→TLV, přistání v Tabuku (30. 9. 2026) – `data/`, `feed*.xml` v kořeni, rutina `/check-fz1073`

Popis níže platí pro stránku každého případu.

- **Pro uživatele:** stránka bez přihlášení, zvýraznění nepřečtených záznamů, stav „přečteno“ v prohlížeči, automatická kontrola nových dat každých 5 minut, přepínač jazyka CZ / SK / EN (volba se pamatuje v prohlížeči, odkaz lze sdílet s `?lang=sk|en|cs`), RSS odběr pro každý jazyk (`feed.xml`, `feed-sk.xml`, `feed-en.xml`), záložka **Foto & video** se všemi médii ze záznamů (duplicity sloučené, filtry typ / status / zdroj / jen nové, stav „zhlédnuto“ per uživatel) a záložka **Zdroje** se seznamem všech sledovaných zdrojů.
- **Pro správce:** data v `<data_dir>/updates.json` případu, aktualizace přes Claude Code příkazem `/check-<id>`. Nový případ: viz CLAUDE.md, sekce „Případy“.

## 1. Zprovoznění (jednorázově)

```bash
cd News_agregator
git init -b main
git add .
git commit -m "FZ1073 monitor: výchozí stav"
gh repo create News_agregator --public --source=. --push
```

Bez GitHub CLI: založte prázdné veřejné repo `News_agregator` na github.com a pak:

```bash
git remote add origin https://github.com/tomasdrobnik/News_agregator.git
git push -u origin main
```

**GitHub Pages:** repo → *Settings* → *Pages* → *Source: Deploy from a branch* → `main` / `/ (root)` → *Save*.

**RSS adresa:** v `config.json` nastavte `site_url` na skutečnou adresu Pages, potom:

```bash
python3 scripts/build_feed.py
git commit -am "Nastavena adresa webu" && git push
```

Uživatelům pošlete odkaz na stránku. RSS si přidají přes odkaz „RSS odběr“ v záhlaví.

## 2. Ruční kontrola v Claude Code

```bash
cd News_agregator
claude
```
a v Claude Code zadejte `/check-fz1073`.

## 3. Automatická kontrola každou hodinu

Běží jako cloudová rutina v Claude (claude.ai/code/routines) – počítač nemusí být zapnutý. Každou celou hodinu (UTC) spustí `/check-fz1073` nad tímto repem. Commit a push proběhne **jen při nových záznamech**. Ten aktualizuje RSS (`feed.xml`) a otevřené stránky to do 5 minut zobrazí (banner, počet v titulku, volitelně systémové upozornění prohlížeče přes tlačítko „Zapnout upozornění“).

## Struktura

| Soubor | Účel |
|---|---|
| `cases.json` | registr případů (cesty, názvy, popisy RSS) |
| `index.html` | rozcestník případů |
| `case.html` | stránka případu (`?c=<id>`) |
| `<data_dir>/updates.json` | data případu (jediný zdroj pravdy) |
| `<data_dir>/sources.json` | registr sledovaných zdrojů případu, kontrola ho sama rozšiřuje |
| `feed.xml`, `feed-sk.xml`, `feed-en.xml` (v `feed_dir`) | RSS případu (CZ/SK/EN), generuje `scripts/build_feed.py`, needitovat |
| `config.json` | adresa webu |
| `CLAUDE.md` | kontext případů a pravidla obsahu pro Claude Code |
| `.claude/commands/check-<id>.md` | rutina kontroly zdrojů případu |

## Upozornění
- Obsah je veřejný. Záznamy „Média“ a „Neověřeno“ nejsou oficiálně potvrzené a stránka to uvádí v záhlaví.
- AvHerald a ASN blokují automatické čtení. Změny v nich se zachytí jen přes vyhledávání, se zpožděním nebo vůbec.
- Stránka nesbírá žádné osobní údaje. Stav „přečteno“ je čistě lokální v prohlížeči každého uživatele (localStorage), na server se nic neposílá. Co si přečte jeden uživatel, zůstává pro ostatní „Nové“ (platí i pro různá zařízení/prohlížeče téhož uživatele). Google Fonts však načítá písma z Google serverů, a tím mu předává IP adresu návštěvníka. Pokud to nechcete, odstraňte `<link>` na fonts.googleapis.com z `index.html`, stránka použije systémová písma.
