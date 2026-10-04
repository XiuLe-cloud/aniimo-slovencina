# Zdrojové nástroje a prekladové dáta

Archív [ANIIMO-Slovencina-zdroje-0.05.zip](ANIIMO-Slovencina-zdroje-0.05.zip) dopĺňa verejnú distribúciu o upraviteľný snapshot prekladu **0.05**, zdroj inštalátora **1.3** a používané kontroly. Hráči ich na inštaláciu nepotrebujú; postup pre hráčov je v README.

Najprv rozbaľ ZIP a otvor priečinok `aniimo-slovencina-source`. Všetky cesty a príkazy nižšie sa vzťahujú na tento rozbalený priečinok. Pre rýchle prezeranie sú samostatne dostupné aj [dáta](translations.sk.json) a [zdroj GUI](Installer-1.3.cs).

## Obsah

- `data/translations.sk.json`: všetkých 112264 záznamov; kľúč → anglický `source` a slovenský `translation`. Obsah zodpovedá vydaniu 0.05, nie tvrdeniu o úplnej jazykovej revízii.
- `data/glossary.json`: terminológia používaná pri kontrole.
- `data/manifest-0.05.json`: zostava, textová verzia a SHA-256 vydaných dát.
- `installer/Installer.cs`: zdroj vydaného GUI 1.3. `PAYLOAD_SHA256` dopĺňa zostavenie.
- `package/`: skutočné skripty pribalené k inštalátoru 1.3, vrátane inštalácie, aktualizácie, kontroly stavu, záloh a obnovy. Jeho pribalený manifest zostáva 0.04; online preklad má vlastnú verziu 0.05.
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

Výstup v `dist/text-0.05/` obsahuje `Compress_en.bin` a `NewTextMap_en.json`. Nástroj skontroluje značky, čísla a spätné dekódovanie. Pre nezmenený snapshot vypíše aj porovnanie hashov s verejným vydaním. Súbory sa nemajú ručne kopírovať do hry; balenie a inštalátor zabezpečujú synchronizáciu archívov aj zálohy.

## Zostavenie aktualizačného balíka

Pripravený priečinok musí obsahovať `manifest.json` a všetky súbory `data/` uvedené v `payloadFiles`. Textový pár nestačí: vydanie obsahuje aj upravené písma a ďalšie lokalizačné dáta. Tie sú vo verejnom vydanom ZIPe, nie v zdrojovej vetve. Pred ich použitím over SHA-256 podľa vydania; žiadny stiahnutý program netreba spúšťať.

```text
python build_update.py --package dist/package --output dist/online --base-url https://github.com/XiuLe-cloud/aniimo-slovencina/releases/download/v0.05
```

Pri vlastných opravách použi novú verziu, prepočítaj hashe dát a vykonaj testy. Príkaz sám nič nepublikuje. Nikdy neprepisuj obsah už publikovanej verzie.

## Zostavenie inštalátora

Windows s .NET Framework kompilátorom `csc.exe` v `Microsoft.NET/Framework64/v4.0.30319`. ZIP musí mať vrchný priečinok `Aniimo-SK-3634150-strojovy-preklad`, ktorý obsahuje `package/` skripty, manifest a kompletné `data/`. Toto je iný formát než dátový online ZIP bez skriptov.

```powershell
.\build_installer.ps1 -PackageZip .\dist\installer-payload.zip -Manifest .\dist\package\manifest.json
```

Zdroj je pre inštalátor 1.3 a zostavu 3634150; nejde zatiaľ o univerzálny inštalátor. Bežná rekompilácia nezaručuje identický hash EXE. Tento upload nemení distribuované EXE ani jeho bezpečnostné hodnotenie.

## Obmedzenia a prispievanie

Historická funkcia `pipeline.engine.initialize` potrebuje pôvodné interné snapshoty 3616231/3629693, ktoré nie sú súčasťou verejného exportu; nepoužívaj ju na import súčasnej 0.05. Verejný podporovaný postup kontroly aktuálnych dát je `build_text_data.py`. Syntetické testy nepotrebujú hru ani internú databázu.

Angličtina je rozhodujúca. Taliansky projekt Sici29/Aniimo-Italian-Translation slúži iba ako sekundárna referencia; jeho korpus ani nástroje nie sú súčasťou tohto exportu. Pri návrhu opravy uveď ID, anglický originál, slovenský návrh a herný kontext. Preklad upravuj v samostatnej vetve, nikdy v zálohách hry.

Zverejnené nie sú súkromné nastavenia, lokálna databáza pamäte, osobné reporty, pôvodné archívy hry ani zálohy používateľa. Plná rekonštrukcia fontov/obrázkov z pôvodnej hry nie je súčasťou tohto zdrojového exportu.

## Práva

Preklad zostáva neoficiálny a bezplatný. Zverejnenie zdrojov samo osebe neudeľuje všeobecnú open-source licenciu. Práva k hre, anglickým textom, značkám a grafike zostávajú ich vlastníkom. Tento dokument neudeľuje práva k obsahu tretích strán; osobitná licencia vlastných nástrojov zatiaľ nebola zvolená.
