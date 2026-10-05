# Changelog

## Translation 0.06 / Installer 1.4 — 2026-10-05

### Preklad
- Schválené HIGH opravy: 4 386 ID.
- Schválené MEDIUM opravy: 675 skupín / 1 206 ID.
- Samostatná oprava ID 2030994140: opis Dance Power, spotreby EP a liečenia; správna poloha percenta pri dynamickej hodnote.
- Spolu 5 593 schválených zmien ID oproti snapshotu 0.05.
- Opravy významu, gramatiky, slovosledu, terminológie a zjavného strojového prekladu. Vlastné názvy a nevyriešené kontextové prípady sa nedopĺňali odhadom.
- Technické overenie celého korpusu; LOW a NEEDS_CONTEXT pokračujú. Nejde o tvrdenie 100 % manuálnej kontroly ani kontroly každého textu v hre.
- In-game test: PASS — správca projektu potvrdil funkčnosť Installer 1.4 a prekladu 0.06 priamo v ANIIMO.

### Installer 1.4
- Spoločná bezpečnostná vrstva pre cieľové cesty, rozbaľovanie, zápisy, zálohy, rollback a obnovu. Odmietanie reparse points a hardlinkov; ochrana otvorených ciest počas operácií.
- Zachované SHA-256, allowlist súborov, kontrola zostavy a zálohovací model.
- Číslo prekladu ostáva nezávislé od installera; online metadata podporujú ďalšie kompatibilné lokalizačné balíky bez nového EXE.
- Pribalená verzia a údaj o zostave v GUI sa generujú pri zostavení. Installer samotný sa neaktualizuje online.
- Pre získanie opravy je potrebné nové EXE 1.4, nie iba aktualizácia textového ZIPu.

## Translation 0.05 / Installer 1.3
- 1 010 úprav textov stôp, predmetov, správy domova a označení úrovne karavanu.
- Zverejnené prekladové dáta a zdrojové nástroje.

## Translation 0.04 / Installer 1.3
- Podpora zostavy 3634150 a online aktualizácie dátového balíka oddelené od verzie EXE.
