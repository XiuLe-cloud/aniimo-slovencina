> Aktuálne vydanie: Translation 0.07, Installer 1.4.1, build 3668494. Manifest 0.07: data/manifest-0.07.json. Staršie manifesty zostávajú historickým záznamom.

# Zdrojové nástroje a prekladové dáta

Tento adresár dopĺňa verejnú distribúciu o upraviteľný snapshot prekladu **0.07**, zdroj inštalátora **1.4.1** a používané kontroly. Hráči ich na inštaláciu nepotrebujú; postup pre hráčov je v README.

## Obsah

- `data/translations.sk.json`: všetkých 112308 záznamov; kľúč → anglický `source` a slovenský `translation`. Obsah je snapshot vydania 0.07 po schválených QA opravách, nie tvrdenie o úplnej jazykovej revízii.
- `data/glossary.json`: terminológia používaná pri kontrole.
- `data/manifest-0.07.json`: zostava, textová verzia a SHA-256 dát vydania.
- `installer/Installer.cs`: zdroj GUI 1.4.1. `PAYLOAD_SHA256` dopĺňa zostavenie.
- `package/`: skutočné skripty pribalené k inštalátoru 1.4.1, vrátane inštalácie, aktualizácie, kontroly stavu, záloh a obnovy. Pribalený manifest je 0.07; online preklad má nezávislú verziu.
- `pipeline/`: implementácia prekladovej pamäte, diffu, ochrany ručných opráv, QA a tvorby kandidátov; `pipeline/tests/` obsahuje syntetické testy.
- `translate_all.py`: lokálny strojový preklad; voliteľne vyžaduje CTranslate2, SentencePiece a samostatný kompatibilný EN→SK model. Model nie je pribalený ani automaticky sťahovaný.
- `build_update.py`: dátový ZIP a version.json z pripraveného balíka.
- `build_text_data.py`: bezpečné zostavenie textových dát bez zápisu do hry.
- `build_installer.ps1`: kompilácia Windows GUI s explicitne zadaným ZIPom a manifestom.

## Kontrola a zostavenie textov

Python 3.10 alebo novší, štandardná knižnica postačuje na QA a testy:

```text
python -m unittest discover -s pipeline/tests -p "test_*.py"
python build_text_data.py
```

Výstup v `dist/text-0.07/` obsahuje `Compress_en.bin` a `NewTextMap_en.json`. Nástroj skontroluje značky, čísla a spätné dekódovanie. Pre nezmenený snapshot vypíše aj porovnanie hashov s aktuálnym manifestom. Súbory sa nemajú ručne kopírovať do hry; balenie a inštalátor zabezpečujú synchronizáciu archívov aj zálohy.

## Zostavenie aktualizačného balíka

Pripravený priečinok musí obsahovať `manifest.json` a všetky súbory `data/` uvedené v `payloadFiles`. Textový pár nestačí: vydanie obsahuje aj upravené písma a ďalšie lokalizačné dáta. Tie sú vo verejnom vydanom ZIPe, nie v zdrojovej vetve. Pred ich použitím over SHA-256 podľa vydania; žiadny stiahnutý program netreba spúšťať.

```text
python build_update.py --package dist/package --output dist/online --base-url https://github.com/XiuLe-cloud/aniimo-slovencina/releases/download/v0.07
```

Pri vlastných opravách použi novú verziu, prepočítaj hashe dát a vykonaj testy. Príkaz sám nič nepublikuje. Nikdy neprepisuj obsah už publikovanej verzie.

## Zostavenie inštalátora

Windows s .NET Framework kompilátorom `csc.exe` v `Microsoft.NET/Framework64/v4.0.30319`. ZIP musí mať vrchný priečinok `Aniimo-SK-package`, ktorý obsahuje `package/` skripty, manifest a kompletné `data/`. Toto je iný formát než dátový online ZIP bez skriptov.

```powershell
.\build_installer.ps1 -PackageZip .\dist\installer-payload.zip -Manifest .\dist\package\manifest.json
```

Zdroj je pre inštalátor 1.4.1 s dôveryhodným základom zostavy 3668494. Budúce verzie prekladu na rovnakom základe fungujú bez nového EXE; zmena základných súborov hry alebo allowlistu vyžaduje nové overenie a môže vyžadovať nový installer. Bežná rekompilácia nezaručuje identický hash EXE. Zmena zdrojov nemení už distribuované EXE 1.3; bezpečnostnú opravu obsahuje až nové EXE 1.4.1.

## Obmedzenia a prispievanie

Historická funkcia `pipeline.engine.initialize` potrebuje pôvodné interné snapshoty 3616231/3629693, ktoré nie sú súčasťou verejného exportu; nepoužívaj ju na import súčasnej 0.07. Verejný podporovaný postup kontroly aktuálnych dát je `build_text_data.py`. Syntetické testy nepotrebujú hru ani internú databázu.

Angličtina je rozhodujúca. Taliansky projekt Sici29/Aniimo-Italian-Translation slúži iba ako sekundárna referencia; jeho korpus ani nástroje nie sú súčasťou tohto exportu. Pri návrhu opravy uveď ID, anglický originál, slovenský návrh a herný kontext. Preklad upravuj v samostatnej vetve, nikdy v zálohách hry.

Zverejnené nie sú súkromné nastavenia, lokálna databáza pamäte, osobné reporty, pôvodné archívy hry ani zálohy používateľa. Plná rekonštrukcia fontov/obrázkov z pôvodnej hry nie je súčasťou tohto zdrojového exportu.

## Práva

Preklad zostáva neoficiálny a bezplatný. Zverejnenie zdrojov samo osebe neudeľuje všeobecnú open-source licenciu. Práva k hre, anglickým textom, značkám a grafike zostávajú ich vlastníkom. Tento dokument neudeľuje práva k obsahu tretích strán; osobitná licencia vlastných nástrojov zatiaľ nebola zvolená.

## Rozdelenie a bezpečné publikovanie

- `data/`: produkčný EN/SK snapshot, slovník a manifesty.
- `installer/`: GUI; `package/`: bezpečnostná vrstva a inštalačné/aktualizačné skripty.
- `pipeline/`: dátové a QA nástroje, automatické testy.
- `qa/`: stručné verejné výsledky a pravidlá, bez pracovných checkpointov či osobných ciest.
- `assets/`: ikona a obrázok GUI. Koreň: dokumentácia, version.json a potrebné build vstupy.

Výstupy `dist/`, lokálne `verification/`, cache, zálohy, databázy a konfigurácie s tajnými údajmi sa nepublikujú do zdrojovej vetvy. Použi `.gitignore` a skontroluj zoznam súborov pred publikovaním; ignore neodstráni už sledovaný citlivý súbor. Nepublikuj nadradený pracovný priečinok.

Online ZIP obsahuje iba manifest a 8 povolených dátových súborov. Pre budúcu 0.08 aktualizuj verziu a hashe v manifeste, zostav ZIP, prepočítaj SHA-256 a aktualizuj feed. Nemeň číslo installera iba kvôli prekladu. Pri novej zostave hry nikdy iba neprepíš číslo buildu.

Regresný Windows test `pipeline/tests/test_installer_14.ps1` vyžaduje izolované lokálne vstupy, celý balík a loopback HTTP feed cez parametre Fixture, Package a FeedBase. Nepúšťaj ho proti živej hre. Pôvodné anglické binárne súbory nie sú súčasťou zdrojového exportu.
