# FZ1073 Incident Monitor

Statický dashboard pro GitHub Pages sledující incident flydubai FZ1073 (30. 9. 2026).

- **Pro uživatele:** stránka bez přihlášení, zvýraznění nepřečtených záznamů, stav „přečteno“ v prohlížeči, automatická kontrola nových dat každých 5 minut, RSS odběr (`feed.xml`), záložka **Foto & video** se všemi médii ze záznamů (duplicity sloučené, filtry typ / status / zdroj / jen nové).
- **Pro správce:** data v `data/updates.json`, aktualizace přes Claude Code příkazem `/check-fz1073`.

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

Vyberte jednu možnost:

**a) Naplánovaná úloha v Claude (bez vlastního počítače)**
Požádejte Clauda v konverzaci, ať vytvoří hodinovou naplánovanou úlohu s připojeným repem `tomasdrobnik/News_agregator` (s právem push) a promptem `Spusť /check-fz1073`.

**b) Váš Mac přes cron** (běží jen když je Mac zapnutý):
```bash
crontab -e
```
```cron
31 * * * * cd ~/GitHub/News_agregator && /usr/local/bin/claude -p "/check-fz1073" >> ~/GitHub/News_agregator.log 2>&1
```
Cestu ke `claude` ověřte příkazem `which claude`. Neinteraktivní režim může vyžadovat předem povolené nástroje. Ty jsou v hlavičce `.claude/commands/check-fz1073.md`, případně je doplňte do `.claude/settings.json`.

## Struktura

| Soubor | Účel |
|---|---|
| `index.html` | stránka dashboardu |
| `data/updates.json` | data (jediný zdroj pravdy) |
| `feed.xml` | RSS, generuje `scripts/build_feed.py`, needitovat |
| `config.json` | adresa webu a popis feedu |
| `CLAUDE.md` | kontext incidentu a pravidla obsahu pro Claude Code |
| `.claude/commands/check-fz1073.md` | rutina kontroly zdrojů |

## Upozornění
- Obsah je veřejný. Záznamy „Média“ a „Neověřeno“ nejsou oficiálně potvrzené a stránka to uvádí v záhlaví.
- AvHerald a ASN blokují automatické čtení. Změny v nich se zachytí jen přes vyhledávání, se zpožděním nebo vůbec.
- Stránka nesbírá žádné osobní údaje. Stav „přečteno“ zůstává v prohlížeči uživatele (localStorage). Google Fonts však načítá písma z Google serverů, a tím mu předává IP adresu návštěvníka. Pokud to nechcete, odstraňte `<link>` na fonts.googleapis.com z `index.html`, stránka použije systémová písma.
