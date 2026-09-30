---
description: Zkontroluj zdroje k incidentu FZ1073, doplň nové záznamy, přegeneruj RSS a pushni
allowed-tools: WebSearch, WebFetch, Read, Edit, Write, Bash(python3 scripts/build_feed.py), Bash(git add:*), Bash(git checkout:*), Bash(git commit:*), Bash(git push:*), Bash(git pull:*), Bash(git status:*), Bash(date:*)
---

Proveď jednu kontrolu incidentu FZ1073 podle pravidel v CLAUDE.md.

1. `git pull --rebase` a zjisti aktuální čas: `date -u +%Y-%m-%dT%H:%M:%SZ`.
2. Načti `data/updates.json`. Zapamatuj si existující záznamy (url + obsah), ať nevznikají duplicity.
3. Zkontroluj zdroje:
   - Načti `data/sources.json` a zkontroluj **všechny** zdroje s `"active": true`: `access: "webfetch"` přes WebFetch, `access: "websearch"` jen přes WebSearch.
   - WebSearch (AvHerald a ASN jen takto): `avherald flydubai A6-FKF`, `aviation-safety.net 582792`, `flydubai FZ1073`, `FZ1073 investigation`, `flydubai statement FZ1073`, `GCAA flydubai`, `GACA Tabuk flydubai`, `A6-FKF`.
   - Přednost mají oficiální zdroje: flydubai, GCAA, GACA/AIB KSA, izraelské úřady. Pak renomovaná média (Reuters, AP, Ynet, Times of Israel, JPost, AvHerald, ASN).
   - **Hledání nových zdrojů:** prohledej web (WebSearch, EN + AR + HE klíčová slova, např. `flydubai Tabuk`, `A6-FKF investigation`, `GACA AIB flydubai`, `Reuters flydubai`, `Times of Israel flydubai`) a najdi další důvěryhodné zdroje, které v `data/sources.json` ještě nejsou. Přidej jen ověřitelné zdroje: oficiální orgány, renomovaná média/agentury, primární data, uznávané letecké weby. Nepřidávej anonymní účty, agregátory kopírující cizí text ani fóra. Nový zdroj zapiš do `sources.json` (`name`, `url`, `type` official|data|media|database, `access`, `added_at` = teď, `active: true`, `note` proč je relevantní). Od příští kontroly se monitoruje automaticky. Každý web, který citujete v novém záznamu, musí být v `sources.json` (web zobrazuje registr v záložce Zdroje).
   - Zdroj, který je trvale nedostupný nebo se ukázal jako nespolehlivý, nemaž: nastav `"active": false` a do `note` napiš důvod.
4. U nalezených fotek a videí nejdřív ověř duplicity: stejné médium se často šíří pod různými URL (twitter.com/x.com, youtu.be/youtube.com, zmenšené verze obrázků, sledovací parametry). Pokud už v datech je, znovu ho nepřidávej. Pokud je podstatné i v novém záznamu, ponech stejnou URL; web ho sloučí. U nového média zjisti přes WebFetch `og:image` a popisek/autora a vyplň `thumb` a `credit` podle CLAUDE.md.
5. Za každou **skutečně novou nebo změněnou** informaci přidej záznam do `updates` (nové `id`, `found_at` = teď, status podle CLAUDE.md). Vyplň i `i18n` s překladem do SK a EN (viz CLAUDE.md). Nic ručně neověřuje: když si nejsi jistý statusem, dej `unconfirmed`. `official`/`data` jen při přímém přečtení zdroje (WebFetch uspěl). Nové prohlášení, oprava, stav šetření, předběžná zpráva, nové foto/video.
6. Aktualizuj `meta`: `last_check` = teď, `next_check` = teď + 1 h, `new_count` = počet přidaných.
7. Spusť `python3 scripts/build_feed.py`. Pokud selže, oprav data a spusť znovu. Upozornění na duplicity projdi a zbytečné záznamy odstraň.
8. Commit a push:
   - nové záznamy: `git add data/ feed*.xml && git commit -m "FZ1073: +N aktualizací (HH:MMZ)"` (pokud přibyly zdroje, přidej do zprávy `, +M zdrojů`)
   - jen nové zdroje bez nových záznamů: commitni a pushni jen `data/sources.json` (`FZ1073: +M zdrojů (HH:MMZ)`), `updates.json` a `feed*.xml` vrať
   - nic nového: **necommituj a nepushuj** (zahoď lokální změnu `meta`: `git checkout -- data/ feed*.xml`). Push = signál pro RSS a upozornění na webu, proto jen při nových záznamech.
9. Na závěr stručně česky vypiš nové záznamy (status, co se změnilo, zdroj). Pokud nic nového, napiš jen „Beze změn“.
10. Pokud vyšla finální zpráva nebo 72 h nepřibylo nic nového, upozorni na to a navrhni snížit frekvenci kontrol.
