# ANIIMO Slovenčina od Xiu_Le

Neoficiálny slovenský preklad. Aktuálna testovacia verzia prekladu: **0.02**.
Podporovaná zostava hry: **3616231**. Verzia inštalátora: **1.0**.

## Vyhlásenie k verejnej lokalizácii

ANIIMO Slovenčina od Xiu_Le je neoficiálny fanúšikovský projekt, ktorého cieľom je sprístupniť hru slovenským hráčom. Nie je oficiálnou súčasťou hry ani lokalizáciou vydanou či schválenou jej vývojármi alebo vydavateľom. Názov ANIIMO, herný obsah a súvisiace značky patria príslušným vlastníkom.

### AI preklad a ručné opravy

Základ slovenských textov vznikol pomocou strojového prekladu a nástrojov umelej inteligencie (AI). Následne sa priebežne opravuje podľa pôvodných anglických textov, herného kontextu a hlásení hráčov. Ručné pripomienkovanie a cielené úpravy zahŕňajú názvy predmetov a schopností, akcie, opisy, pokyny a ďalšie texty rozhrania; pri spracovaní opráv sa naďalej využíva aj AI.

**Celý preklad zatiaľ neprešiel úplnou ľudskou jazykovou a kontextovou revíziou.** Niektoré texty môžu byť nepresné, neprirodzené, nejednotné alebo zostať v angličtine. Verejné sprístupnenie neznamená, že ide o dokončený profesionálny preklad. Verzia **0.02 je testovacie vydanie**. Lokalizácia neposkytuje slovenský dabing a nemusí pokrývať texty dodávané serverom ani všetky obrázky s textom.

### Čo bolo otestované

Pri zostavení sa kontroluje zachovanie formátovacích značiek a zástupných hodnôt v textoch. Na oddelenej testovacej kópii herných súborov bola overená inštalácia, prechod z prekladu 0.01 na 0.02 a obnova pôvodnej angličtiny. Obnovené súbory sa pri teste zhodovali s originálmi po jednotlivých bajtoch.

Aktualizátor bol otestovaný aj s nesprávnym SHA-256, poškodeným balíkom, nepovoleným obsahom ZIPu, nekompatibilnou zostavou a simulovanou chybou počas zápisu. Overené bolo vrátenie predchádzajúceho stavu aj následná obnova prerušenej operácie. Po zverejnení sa overilo načítanie online manifestu a kontrolný súčet balíka stiahnutého z GitHubu.

Priebežné skúšanie v hre a hlásenia testerov pomáhajú odhaľovať chyby. Tieto kontroly však nie sú potvrdením, že boli prejdené všetky dialógy, úlohy, obrazovky a herné situácie. Najnovšie textové opravy môžu ešte vyžadovať vizuálne overenie v hre.

### Zálohy a bezpečná obnova

Pred prvou inštaláciou sa vytvára záloha pôvodných anglických súborov dotknutých lokalizáciou. Pri aktualizácii sa táto záloha neprepisuje slovenskými súbormi. Funkcia **Obnoviť angličtinu** používa pôvodné originály; nejde o zálohu uloženej hry ani celého herného priečinka.

Pred aktualizáciou sa navyše vytvára dočasná kópia aktuálneho stavu. Ak zápis zlyhá, aktualizátor sa pokúsi obnoviť predchádzajúcu verziu. Ak obnovu znemožní napríklad nedostupný disk alebo zamknutý súbor, potrebné dáta zostanú zachované a pri ďalšom spustení sa ponúkne obnova prerušenej operácie. Počas inštalácie, aktualizácie a obnovy musí byť hra ukončená.

Nové zálohy sa ukladajú do `%LOCALAPPDATA%\AniimoSlovencina\backups`. Podporované sú aj staršie zálohy v priečinku `Aniimo-SK-zaloha` pri hre. Zálohy nemaž ani neupravuj, pokiaľ ich chceš používať na obnovu. Ak sa herné súbory medzitým zmenili, inštalátor môže obnovu odmietnuť, aby starými súbormi neprepísal aktualizovanú hru.

### Kompatibilita a aktualizácie

Toto vydanie je pripravené pre zostavu ANIIMO **3616231**. Ide o označenie zostavy používané hrou, nie o Steam build ID. Kompatibilita s inými zostavami nie je potvrdená. Po aktualizácii hry môže byť potrebný upravený lokalizačný balík alebo nový kompatibilný inštalátor; samotná zmena čísla zostavy v manifeste nestačí.

Inštalátor overuje zostavu aj známe kontrolné súčty súborov. Pri nezhode alebo neznámych zmenách nemá súbory automaticky prepisovať. Súčasná kombinácia s inými úpravami rovnakých súborov nie je overená.

**Verzia prekladu a verzia inštalátora sú oddelené.** Online aktualizácie sťahujú iba lokalizačný balík, overujú jeho SHA-256 a povolený obsah. Samotné EXE sa automaticky neaktualizuje. Kontrolný súčet pomáha overiť neporušenosť balíka, nie jazykovú správnosť prekladu.

## Stiahnutie a inštalácia

[Stiahnuť inštalátor](https://github.com/XiuLe-cloud/aniimo-slovencina/releases/download/v0.02/Aniimo-Slovencina-Instalator-1.0-preklad-0.02.exe)

1. Ukonči ANIIMO a spusti inštalátor.
2. Skontroluj priečinok hry a nainštaluj slovenčinu.
3. V hre ponechaj jazyk **English**.

Inštalátor uchová pôvodnú anglickú zálohu. Tlačidlo **Obnoviť angličtinu** obnoví originály.

## Online aktualizácie

Nové EXE má adresu aktualizácií nastavenú. Pri otvorení alebo po **Skontrolovať znova** overí novú verziu prekladu.
V staršom inštalátore 1.0 môžeš cez **Nastaviť aktualizácie** vložiť:

```text
https://raw.githubusercontent.com/XiuLe-cloud/aniimo-slovencina/main/version.json
```

Pôvodné EXE prekladu 0.01 ešte online aktualizátor nemá; nový inštalátor si stiahni raz.
ZIP pri vydaní je dátový balík pre aktualizátor, nerozbaľuj ho ručne do hry.
Aktualizujú sa iba lokalizačné dáta, nie samotný EXE inštalátor.

## Hlásenie chýb

V [Issues](https://github.com/XiuLe-cloud/aniimo-slovencina/issues) uveď verziu prekladu, zostavu hry, miesto alebo situáciu, v ktorej sa chyba objavila, a prilož snímku nesprávneho textu. Ak môžeš, doplň pôvodný anglický text alebo návrh opravy. Pred odoslaním snímky skontroluj, či neobsahuje osobné údaje.

Ďakujeme všetkým hráčom, ktorí pomáhajú preklad skúšať a zlepšovať.
