# ANIIMO – Slovenská lokalizácia 🇸🇰

Bezplatná neoficiálna komunitná lokalizácia ANIIMO od Xiu_Le.

**[Stiahnuť Installer 1.4.1 pre preklad 0.07](https://github.com/XiuLe-cloud/aniimo-slovencina/releases/download/v0.07/Aniimo-Slovencina-Instalator-1.4.1-preklad-0.07.exe)** · [Release 0.07 a kontrolné súčty](https://github.com/XiuLe-cloud/aniimo-slovencina/releases/tag/v0.07)

| Údaj | Stav |
|---|---|
| Translation | **0.07** |
| Installer | **1.4.1** |
| Podporovaná zostava hry | **3668494** (označenie hry, nie Steam build ID) |
| HIGH QA | **Dokončená** |
| MEDIUM QA | **Dokončená** |
| Technical QA | **PASS** |
| In-game test | **PASS — potvrdené správcom projektu** |
| LOW QA a NEEDS_CONTEXT | **Pokračujú** |

## Pôvod a kvalita prekladu

Základ vznikol pomocou AI/strojového prekladu (MT). Následne prešiel systematickou jazykovou a kontextovou QA voči anglickému originálu, technickými kontrolami a testovaním v hre. Kontextovo nejasné prípady zostávajú odložené. Správca projektu potvrdil funkčnosť Installer 1.4.1 a prekladu 0.07 priamo v ANIIMO. Pri príprave a opravách sa naďalej používa AI a ľudské schvaľovanie návrhov. Nie je pravda, že celý preklad je 100 % manuálne skontrolovaný.

- **HIGH QA dokončená:** aplikovaných 4 386 schválených ID; odložené kontextové prípady zostávajú oddelené.
- **MEDIUM QA dokončená:** aplikovaných 675 schválených skupín / 1 206 ID.
- **Technická QA dokončená:** celý korpus 112 308 záznamov; samostatne opravené ID 2030994140.
- **LOW a NEEDS_CONTEXT pokračujú.** Nejasné návrhy sa neaplikovali.

Dokončenie QA fázy neznamená úplné otestovanie všetkých dialógov, obrazoviek, herných mechaník ani serverových textov. Podrobnosti a hranice overenia sú v [QA pre 0.07](qa/RELEASE_0.07.md).

## Inštalácia a aktualizácie

Súbory verzie 0.07 sú v [GitHub Release 0.07](https://github.com/XiuLe-cloud/aniimo-slovencina/releases/tag/v0.07). Bežnému hráčovi stačí EXE; dátový ZIP sťahuje updater automaticky.

Použi Installer **1.4.1**, ktorý posilňuje ochranu cieľových ciest. Pri prechode z 0.06 na nový build si jednorazovo stiahni EXE 1.4.1. Pôvodný Installer 1.4 nový herný základ nepodporuje. Zálohy zachovaj; overené pôvodné assety zo zálohy build-3634150 installer bezpečne rozpozná.

1. Ukonči hru a spusti installer.
2. Vyber priečinok podporovanej hry; pri čistej inštalácii použi **Nainštalovať slovenčinu** alebo ponúknutý online balík.
3. Pri aktualizácii klikni na **Skontrolovať znova** a potom na **Aktualizovať na …**. Samotná kontrola nič neinštaluje.
4. V hre nechaj jazyk **English**.

Installer 1.4.1 a preklad majú nezávislé verzie. Ďalšie preklady 0.08, 0.09 atď. môže rovnaký installer sťahovať cez metadata bez nového EXE, pokiaľ zachovávajú dôveryhodný základ hry a povolené súbory. Nové funkcie, bezpečnostná logika alebo nový nekompatibilný základ hry môžu vyžadovať nový installer.

Online zdroj je `https://raw.githubusercontent.com/XiuLe-cloud/aniimo-slovencina/main/version.json`. Feed určuje verziu prekladu, zostavu, URL a SHA-256 dátového ZIPu. Installer overuje tieto údaje aj manifest a hashe jednotlivých súborov. ZIP neobsahuje spúšťané aktualizačné skripty. Neprepisuj ručne súbory hry obsahom ZIPu.

## Zálohy a bezpečnosť

Pred prvou inštaláciou sa zachovajú overené anglické originály. Ďalšie aktualizácie ich neprepíšu slovenčinou. Pred aktualizáciou vzniká dočasná záloha súčasného stavu pre rollback. **Obnoviť angličtinu** vracia originály; nejde o zálohu uloženej hry.

Installer odmieta presmerované cesty (junction/symlink/reparse point), nepovolený obsah ZIPu a nezhodné kontrolné súčty. Konzervatívne môže odmietnuť aj legitímny synchronizovaný alebo presmerovaný priečinok; nepovažuj ho za podporovanú inštalačnú cestu. Použi bežný lokálny priečinok. Zálohy nemaž. Pri prerušenej operácii zachovaj dáta a použi ponúknutú obnovu.

SHA-256 overuje neporušenosť, nie dôveryhodnosť autora ani neprítomnosť škodlivého kódu. EXE momentálne nie je digitálne podpísané a Windows môže zobraziť bezpečnostné upozornenie; nulové antivírusové detekcie sa negarantujú. Feed aj balíky musia zostať pod kontrolou správcu projektu.

## Kompatibilita

Vydanie je zostavené nad overenými vstupnými súbormi zostavy **3668494**. Kompatibilita s inými alebo budúcimi zostavami nie je potvrdená. Aktuálnosť živej verzie hry sa z tohto čísla neodvodzuje. Zmena čísla zostavy vo feede sama osebe nestačí na bezpečnú podporu nových herných súborov.

## Hlásenie chýb

Použi [Discord Aniimo CZ/SK](https://discord.gg/ygN2cWJmRW), fórum [chyby-prekladu](https://discord.com/channels/1546824435770720256/1554686019599859742), prípadne [GitHub Issues](https://github.com/XiuLe-cloud/aniimo-slovencina/issues). Uveď verziu prekladu, game build, miesto výskytu a snímku bez osobných údajov; pomôže aj anglický originál a ID.

## Zdroje a práva

[SOURCE.md](SOURCE.md) opisuje zostavenie, [CHANGELOG.md](CHANGELOG.md) zmeny a [qa/](qa/) verejné výsledky kontrol. Pracovné zálohy, checkpointy a lokálne logy nie sú súčasťou verejného zdrojového balíka.

Projekt nie je vydaný ani schválený vývojármi či vydavateľom ANIIMO. Preklad a installer sú pre hráčov bezplatné; hru si zabezpečuje hráč samostatne. Práva k hre, anglickým textom, značkám a grafike zostávajú ich vlastníkom. Zverejnenie zdrojov neudeľuje všeobecnú open-source licenciu; osobitná licencia vlastných nástrojov zatiaľ nebola zvolená.
