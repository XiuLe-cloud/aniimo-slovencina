# Overenie vydania 0.07 / Installer 1.4.1

Build 3668494, 112 308 záznamov. Používateľ potvrdil funkčnosť prekladu priamo v hre; nejde o úplnú vizuálnu ani jazykovú kontrolu všetkých textov.

- 31 offline Python testov PASS.
- 31 inštalačných/update/rollback/restore a bezpečnostných regresií PASS; 9 migračných kontrol PASS.
- Dve dodatočné junction kontroly finálneho SafePath PASS, 0 zápisov mimo cieľa.
- Samostatný symlink test NOT_RUN: Windows nepovolil vytvorenie odkazu. Ekvivalentná spoločná ochrana overená reálnym junction testom a kontrolou kódu: Validate odmieta FileAttributes.ReparsePoint; Open odmieta atribút 0x400 získaný z otvoreného handle. Nerozlišuje ani nepovoľuje konkrétny reparse tag. Toto nie je tvrdenie o vykonaní symlink testu.
- Celý textový korpus: core QA bez ERROR, binárny roundtrip a SHA-256 textových súborov PASS. Šesť historických odchýlok prísneho poradia zostáva nezmenených; žiadne nové.
- Všetkých 18 chránených textov a 112 165 nezmenených prekladov zachovaných.
- Šesť kontextových ID schválených používateľom; deväť zostáva na kontrolu vrátane Pack.
- Finálne EXE: 19 rozbalených súborov zhodných s vydávaným balíkom.
- Budúci kompatibilný update 0.07 → 0.08 rovnakým installerom: PASS v izolovanom teste. Iný build alebo nezhodný základ je odmietnutý.

## Známa vizuálna neistota

Používateľ hlási žlté zátvorky a rozdielne vertikálne rozloženie mien/ikoniek pri Aniimo. Dve uvedené snímky nie sú v aktuálnom vstupe dostupné a chýba porovnanie tej istej scény v EN a SK. Príčinu nemožno pripísať lokalizácii, fontu ani pôvodnému UI. Rozloženie hry sa nemenilo. Potrebné je porovnanie rovnakej scény a nastavení. Fontový payload 0.07 zostáva zhodný s 0.06; to nevylučuje starší fontový vplyv.
