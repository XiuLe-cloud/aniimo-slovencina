# QA vydania 0.06 / Installer 1.4

Stav: **schválené vydanie; in-game test PASS potvrdený správcom projektu 2026-10-05**. Základ hry 3634150, textová verzia 1790825290. Nejde o potvrdenie aktuálnosti živej hry.

- HIGH QA uzavretá: 4 386 schválených ID; MEDIUM uzavretá: 675 skupín / 1 206 ID. Samostatne schválené ID 2030994140. Spolu 5 593 rozdielnych ID oproti 0.05.
- V tejto príprave sa produkčné texty jazykovo nemenili. 112 264 ID, ich poradie a anglické originály zachované. Chránené QA archívy overené hashmi, záloha zdrojov 1.3 zachovaná lokálne.
- Celý korpus: nulové blokujúce technické chyby, kontrola tagov/premenných/čísel/percent a spätného načítania textových dát. Šesť predtým manuálne vyhodnotených rozdielov spoločného poradia čísel zostáva bez zmeny; súvisia so slovenským slovosledom/formátovaním.
- LOW a NEEDS_CONTEXT pokračujú. Angličtina je autoritatívna; nejasné opravy neboli aplikované. Dokončenie QA fázy neznamená 100 % manuálnu revíziu.

## Výsledky inštalátora

Windows PowerShell 5.1, izolované kópie vstupov a lokálny HTTP server; žiadne zápisy do živej hry. **31 PASS, 1 NOT_RUN**. Okrem toho **31 Python unit testov PASS**. Podrobný zoznam: [installer-1.4-results.json](installer-1.4-results.json).

| Kontrola | Výsledok |
|---|---|
| Pôvodný junction reprodukčný test | Odmietnutý; 0 súborov mimo cieľa (v 1.3 bolo 8) |
| Kompilované EXE: bežné rozbalenie / junction | PASS / odmietnuté, 0 súborov mimo cieľa |
| Čistá 0.06 online aj pribalený offline balík | PASS |
| 0.05 → 0.06 | PASS |
| Skontrolovať znova: logika Status s testovacím feedom | Ponuka 0.07 nad nainštalovanou 0.06, PASS |
| Simulovaná 0.06 → 0.07 bez zmeny installera | PASS; iba izolované metadata, nikdy verejná 0.07 |
| Feed, SHA-256, nesprávny build/verzia, poškodený ZIP/dáta | Platný prijatý, chybné odmietnuté bez zmeny hry |
| ZIP traversal / allowlist | Odmietnuté |
| Junction v zápise, zálohe, obnove, cleanup, archíve; hardlink a ADS | Odmietnuté |
| Rollback po chybe po treťom zápise | Súbory, stav a pôvodné zálohy bajtovo identické |
| Restore English po 0.06 aj simulovanej 0.07 | Bajtovo identické anglické originály |
| Samostatný directory symlink | NOT_RUN: Windows odmietol vytvorenie, chyba oprávnenia 1314 |

## Rozdiel 1.3 → 1.4

Spoločná vrstva SafePath pre rozbaľovanie, súborové zápisy, zálohovanie, obnovu a presuny odmieta reparse points a hardlinky. Otvorené operácie držia rodičovské adresáre proti presmerovaniu; súbor sa pred kontrolou jeho handle netrunkuje. Hashovanie používa bezpečne otvorený stream. Existujúci allowlist, HTTPS, SHA-256 a model pôvodnej anglickej zálohy zostávajú zachované.

Verzia prekladu a údaj v GUI sa generujú z manifestu. Online feed a manifest určujú budúci preklad; dôveryhodný základ herných súborov/allowlist zostáva pribalený k EXE. **0.07/0.08 na rovnakom základe nepotrebujú nový installer.** Neznáma zostava hry sa automaticky nepovolí len zmenou čísla vo feede.

## Hranice overenia pred vydaním

- Samostatný symlink test treba dokončiť na Windows s príslušným oprávnením alebo Developer Mode. Junction už precvičil spoločné odmietnutie reparse bitu, ale nenahrádza tento nespustený test.
- Správca projektu potvrdil funkčnosť 0.06 a Installer 1.4 priamo v hre; nejde o kontrolu všetkých herných textov. Proces hry bol v izolovanej sade simulovaný. Výpadok napájania, plný disk a všetky cudzie filesystem providery neboli simulované.
- Presmerované/cloudové priečinky sú konzervatívne odmietané aj pri legitímnom použití. Bežný lokálny adresár je požiadavka bezpečnostnej vrstvy.
- EXE nie je podpísané a tento audit nie je antivírusový certifikát. SHA neoveruje identitu vydavateľa; dôveryhodnosť feedu závisí od HTTPS a správy účtu/úložiska.
- Test feedu prebiehal cez loopback HTTP. Verejný download a aktualizačné metadata sa dodatočne kontrolujú po publikovaní; výsledok je v post-release reporte.
- Online aktualizácia mení lokalizačné dáta, nie už distribuované EXE 1.3. Oprava bezpečnosti vyžaduje jednorazové stiahnutie 1.4.

Zdrojový repozitár obsahuje iba verejné nástroje, dáta a tento stručný report; interné logy, pracovné checkpointy a zálohy zostávajú mimo verejného exportu.
