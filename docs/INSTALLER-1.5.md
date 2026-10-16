# Installer 1.5

## Požiadavky a inštalácia

Windows s Windows PowerShell 5.1, .NET Framework 4.x a Microsoft Edge; nainštalovaná podporovaná verzia ANIIMO cez Steam. Inštalátor používa Edge na zobrazenie rozhrania. Tieto komponenty sú bežne súčasťou Windows; neinštaluj ich z neznámych zdrojov.

1. Stiahni vyššie uvedený EXE z tohto vydania.
2. Ukonči ANIIMO a Steam; inštalátor chráni súbory pred súbežnou aktualizáciou. Ponúka aj korektné ukončenie Steamu po potvrdení.
3. Spusť EXE, vyber **Slovenčina** alebo **Čeština**.
4. Skontroluj skutočný priečinok hry. Ak ho automaticky nenájde, vyber priečinok obsahujúci `Aniimo.exe`, napríklad v Steam knižnici na inom disku.
5. Použi **Znova overiť** a potvrď inštaláciu pribaleného jazyka. Pre online balík použi Aktualizácie a možnosti, skontroluj aktualizácie a potvrď stiahnutie a inštaláciu.
6. Po úspešnom dokončení spusti Steam a ANIIMO. V nastavení hry ponechaj **English**.

Installer obsahuje aktuálne oba jazyky a nevyžaduje vývojový priečinok autora. Lokálne zostaví jazykové Lua archívy z overených herných dát používateľa. Pri inom builde alebo neznámych súboroch inštaláciu odmietne; kontroly neobchádzaj.

## Prepnutie jazyka a obnovenie angličtiny

V rovnakom programe vyber druhý jazyk a vykonaj inštaláciu pribaleného balíka. **Obnoviť angličtinu / Restore English** obnoví všetkých 12 sledovaných originálov vrátane fontov. Nejde o zálohu uložených pozícií ani celej hry.

EN zálohy a stav transakcií sú v `%LOCALAPPDATA%\AniimoInstaller15\instances`. Nemaž ich. Pri hlásení **Pending transaction — recover first** použi **Obnoviť prerušenú transakciu**, potom **Znova overiť**. Pri nezhode buildu alebo chýbajúcej zálohe zastav a nahlás chybu; nemaž ručne `pending.json`.

Cesta `C:\Users\…\AppData\Local\AniimoInstaller15\app` v hlásení je pracovná cache programu, nie cieľová cesta hry. Hra môže byť na D: alebo inom disku.

## Budúce aktualizácie bez nového EXE

Pre kompatibilný balík podporovaného buildu: **Aktualizácie a možnosti → Vybrať aktualizačný ZIP → Nainštalovať overenú aktualizáciu**. Program overí podpis, SHA-256, jazyk a build a pred zápisom zobrazí cieľ. ZIP nerozbaľuj do hry.

Priložené CS a SK aktualizačné ZIPy sú voliteľné a obsahujú rovnaké preklady ako EXE. Installer ich vie stiahnuť z overených kanálov pre build 3732728; kontroluje digitálny podpis, SHA-256, jazyk a kompatibilitu. Na prechod zo zostavy pre 3714366 si **jednorazovo stiahni nový EXE**. Starý EXE sa sám neaktualizuje. Ďalšie kompatibilné jazykové opravy pre podporovaný build nevyžadujú nový EXE. Zmenu buildu hry treba znovu overiť. ZIP nerozbaľuj do hry.

Starý `version.json` ostáva historickým kanálom Installeru 1.4.1. Nie je aktualizátorom tohto vydania. Staršie inštalátory sa samy nezmenia na 1.5.


## Build 3743667
Pre tento build stiahni nový EXE z aktuálneho vydania: https://github.com/XiuLe-cloud/aniimo-slovencina/releases/tag/installer-1.5-build-3743667-test.1
Obsahuje CS 0.04-test.1 a SK 0.10-test.1. Staršie EXE nepodporujú nový build. Oba jazyky sú pribalené, ďalšie kompatibilné jazykové opravy možno stiahnuť online.
