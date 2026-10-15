# ANIIMO CZ/SK od Xiu_Le

Bezplatný **neoficiálny komunitný preklad** ANIIMO do slovenčiny a češtiny.
Projekt nie je oficiálnou lokalizáciou vývojárov ani vydavateľa a nevystupuje v ich mene. Názov ANIIMO, herný obsah a značky patria príslušným vlastníkom. Toto vyhlásenie nepredstavuje potvrdenie ich schválenia projektu ani otvorenú licenciu k herným assetom.

## Čo stiahnuť

**[Stiahnuť Installer 1.5 – čeština aj slovenčina](https://github.com/XiuLe-cloud/aniimo-slovencina/releases/download/installer-1.5-build-3714366-test.1/ANIIMO-Localization-Installer-1.5.exe)**

[Vydanie, voliteľný aktualizačný ZIP a SHA-256](https://github.com/XiuLe-cloud/aniimo-slovencina/releases/tag/installer-1.5-build-3714366-test.1)

Na prvú inštaláciu stačí **jeden EXE**. Oba preklady sú pribalené; netreba samostatný jazykový ZIP, Python, prekladový model, Git, účet GitHub ani sťahovať „Source code“. Preklad je bezplatný.

| Súčasť | Verzia |
|---|---|
| Installer | 1.5 s importom lokálnych aktualizácií |
| Slovenčina | 0.08-test.1 |
| Čeština | 0.02-test.4 |
| Podporovaný build ANIIMO | **3714366** (číslo hry, nie Steam build ID) |
| Záznamy každého jazyka | 112 327 jedinečných ID |
| Stav vydania | Verejná komunitná testovacia verzia |

## Požiadavky a inštalácia

Windows s Windows PowerShell 5.1, .NET Framework 4.x a Microsoft Edge; nainštalovaná podporovaná verzia ANIIMO cez Steam. Inštalátor používa Edge na zobrazenie rozhrania. Tieto komponenty sú bežne súčasťou Windows; neinštaluj ich z neznámych zdrojov.

1. Stiahni vyššie uvedený EXE z tohto vydania.
2. Ukonči ANIIMO a Steam; inštalátor chráni súbory pred súbežnou aktualizáciou. Ponúka aj korektné ukončenie Steamu po potvrdení.
3. Spusť EXE, vyber **Slovenčina** alebo **Čeština**.
4. Skontroluj skutočný priečinok hry. Ak ho automaticky nenájde, vyber priečinok obsahujúci `Aniimo.exe`, napríklad v Steam knižnici na inom disku.
5. Použi **Znova overiť** a potvrď inštaláciu pribaleného jazyka. Nepoužívaj tlačidlo online sťahovania: online kanály pre tento build nie sú aktivované.
6. Po úspešnom dokončení spusti Steam a ANIIMO. V nastavení hry ponechaj **English**.

Installer obsahuje aktuálne oba jazyky a nevyžaduje vývojový priečinok autora. Lokálne zostaví jazykové Lua archívy z overených herných dát používateľa. Pri inom builde alebo neznámych súboroch inštaláciu odmietne; kontroly neobchádzaj.

## Prepnutie jazyka a obnovenie angličtiny

V rovnakom programe vyber druhý jazyk a vykonaj inštaláciu pribaleného balíka. **Obnoviť angličtinu / Restore English** obnoví všetkých 12 sledovaných originálov vrátane fontov. Nejde o zálohu uložených pozícií ani celej hry.

EN zálohy a stav transakcií sú v `%LOCALAPPDATA%\AniimoInstaller15\instances`. Nemaž ich. Pri hlásení **Pending transaction — recover first** použi **Obnoviť prerušenú transakciu**, potom **Znova overiť**. Pri nezhode buildu alebo chýbajúcej zálohe zastav a nahlás chybu; nemaž ručne `pending.json`.

Cesta `C:\Users\…\AppData\Local\AniimoInstaller15\app` v hlásení je pracovná cache programu, nie cieľová cesta hry. Hra môže byť na D: alebo inom disku.

## Budúce aktualizácie bez nového EXE

Pre kompatibilný balík podporovaného buildu: **Aktualizácie a možnosti → Vybrať aktualizačný ZIP → Nainštalovať overenú aktualizáciu**. Program overí podpis, SHA-256, jazyk a build a pred zápisom zobrazí cieľ. ZIP nerozbaľuj do hry.

Priložený `ANIIMO-CS-0.02-test.4-build-3714366-UPDATE.zip` je voliteľný a obsahuje rovnakú češtinu ako EXE. Staré `PREPARED-DATA.zip`, zdrojové ZIPy GitHubu a balíky pre staré inštalátory nie sú týmto formátom. Pri zmene buildu treba nové overenie kompatibility; nesľubujeme podporu všetkých budúcich buildov rovnakým EXE.

Starý `version.json` ostáva historickým kanálom Installeru 1.4.1. Nie je aktualizátorom tohto vydania. Staršie inštalátory sa samy nezmenia na 1.5.

## Kvalita a testovanie

Základ prekladov vznikol pomocou AI/strojového prekladu, nasledujú priebežné opravy podľa EN originálu a herného kontextu. Úplná ľudská revízia všetkých textov nie je dokončená. Nejde o profesionálny ani oficiálny preklad; dabing sa nemení.

- 15 integračných a 10 GUI kontrol finálnej zostavy PASS: inštalácia CS/SK, import, Restore English, rollback a odmietnutie poškodených balíkov.
- Správca projektu osobne potvrdil obnovenie angličtiny a úspešnú inštaláciu slovenčiny. Následná kontrola overila všetkých 12 slovenských súborov a EN zálohy.
- CS test.4 obsahuje 705 opráv oproti test.3, české úvodné upozornenie a podpis „Čeština od Xiu_Le“.
- 20 nejasných českých názvov zostáva na posúdenie; úplná ručná kontrola starších popisov a grafiky v hre pokračuje. Technické testy nezaručujú bezchybný preklad každej obrazovky.

## Obsah a kontrolné súčty

EXE nie je podpísané certifikátom Windows. SHA-256 nájdeš v `SHA256SUMS.txt`; napríklad `Get-FileHash .\ANIIMO-Localization-Installer-1.5.exe -Algorithm SHA256`.

Úplný pôvodný `LuaScripts.xdf` nie je pribalený; jazykový archív vzniká lokálne. Balíky však obsahujú upravené fontové a úvodné herné assety vrátane `resources.assets.resS`, preto nejde o distribúciu výhradne vlastných textov. Práva k pôvodnému hernému obsahu zostávajú jeho vlastníkom.

## Priečinky prekladov a vývoj

- [`languages/cs`](languages/cs): české texty, manifest a poznámky.
- [`languages/sk`](languages/sk): slovenské texty, manifest a poznámky.
- [`docs/INSTALLER-1.5.md`](docs/INSTALLER-1.5.md): stručný návod a riešenie chýb.
- [`qa/RELEASE_1.5_3714366.md`](qa/RELEASE_1.5_3714366.md): overenie aktuálneho vydania.

Staršie zdroje v `installer/`, `package/` a pôvodné build skripty dokumentujú staršie vydania; nie sú návodom na zostavenie nového EXE 1.5. Autoritatívny binárny súbor tohto vydania je v Releases. Exporty JSON sa ručne do hry nekopírujú.

## Hlásenie chýb

[GitHub Issues](https://github.com/XiuLe-cloud/aniimo-slovencina/issues) alebo [Discord Aniimo CZ/SK](https://discord.gg/ygN2cWJmRW). Uveď jazyk, verziu prekladu, build hry, obrazovku/úlohu a screenshot. Nezverejňuj osobné údaje, prihlasovacie údaje ani celé herné archívy.
