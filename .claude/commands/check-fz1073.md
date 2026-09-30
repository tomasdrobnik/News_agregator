---
description: Zkontroluj zdroje k incidentu FZ1073, doplň nové záznamy, přegeneruj RSS a pushni
allowed-tools: WebSearch, WebFetch, Read, Edit, Write, Bash(python3 scripts/build_feed.py), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(git pull:*), Bash(git status:*), Bash(date:*)
---

Proveď jednu kontrolu incidentu FZ1073 podle pravidel v CLAUDE.md.

1. `git pull --rebase` a zjisti aktuální čas: `date -u +%Y-%m-%dT%H:%M:%SZ`.
2. Načti `data/updates.json`. Zapamatuj si existující záznamy (url + obsah), ať nevznikají duplicity.
3. Zkontroluj zdroje:
   - WebFetch: AeroTime a FR24 blog (URL v CLAUDE.md).
   - WebSearch (AvHerald a ASN jen takto): `avherald flydubai A6-FKF`, `aviation-safety.net 582792`, `flydubai FZ1073`, `FZ1073 investigation`, `flydubai statement FZ1073`, `GCAA flydubai`, `GACA Tabuk flydubai`, `A6-FKF`.
   - Přednost mají oficiální zdroje: flydubai, GCAA, GACA/AIB KSA, izraelské úřady. Pak renomovaná média (Reuters, AP, Ynet, Times of Israel, JPost, AvHerald, ASN).
4. U nalezených fotek a videí nejdřív ověř duplicity: stejné médium se často šíří pod různými URL (twitter.com/x.com, youtu.be/youtube.com, zmenšené verze obrázků, sledovací parametry). Pokud už v datech je, znovu ho nepřidávej. Pokud je podstatné i v novém záznamu, ponech stejnou URL; web ho sloučí. U nového média zjisti přes WebFetch `og:image` a popisek/autora a vyplň `thumb` a `credit` podle CLAUDE.md.
5. Za každou **skutečně novou nebo změněnou** informaci přidej záznam do `updates` (nové `id`, `found_at` = teď, status podle CLAUDE.md). Nové prohlášení, oprava, stav šetření, předběžná zpráva, nové foto/video.
6. Aktualizuj `meta`: `last_check` = teď, `next_check` = teď + 1 h, `new_count` = počet přidaných.
7. Spusť `python3 scripts/build_feed.py`. Pokud selže, oprav data a spusť znovu. Upozornění na duplicity projdi a zbytečné záznamy odstraň.
8. Commit a push:
   - nové záznamy: `git commit -am "FZ1073: +N aktualizací (HH:MMZ)"`
   - nic nového: commitni jen změnu `meta` se zprávou `FZ1073: kontrola HH:MMZ, beze změn`
9. Na závěr stručně česky vypiš nové záznamy (status, co se změnilo, zdroj). Pokud nic nového, napiš jen „Beze změn“.
10. Pokud vyšla finální zpráva nebo 72 h nepřibylo nic nového, upozorni na to a navrhni snížit frekvenci kontrol.
