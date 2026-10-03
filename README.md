# ANIIMO Slovenčina od Xiu_Le

Neoficiálny slovenský preklad. Aktuálna testovacia verzia prekladu: **0.05**.
Podporovaná zostava hry: **3634150**. Verzia inštalátora: **1.3**.

## Bezplatné používanie

Slovenský preklad aj inštalátor sú pre hráčov **bezplatné**. Za stiahnutie, používanie ani dostupné aktualizácie prekladu nevyžadujeme platbu alebo predplatné. Na stiahnutie z verejného GitHub vydania nepotrebuješ účet ani členstvo na Discorde.

Preklad vyžaduje samostatne nainštalovanú podporovanú verziu ANIIMO. Bezplatné sprístupnenie prekladu nemení práva k samotnej hre ani neznamená udelenie otvorenej licencie k jej obsahu.

## Vyhlásenie k verejnej lokalizácii

ANIIMO Slovenčina od Xiu_Le je neoficiálny fanúšikovský projekt, ktorého cieľom je sprístupniť hru slovenským hráčom. Nie je oficiálnou súčasťou hry ani lokalizáciou vydanou či schválenou jej vývojármi alebo vydavateľom. Názov ANIIMO, herný obsah a súvisiace značky patria príslušným vlastníkom.

### AI preklad a ručné opravy

Základ slovenských textov vznikol pomocou strojového prekladu a nástrojov umelej inteligencie (AI). Následne sa priebežne opravuje podľa pôvodných anglických textov, herného kontextu a hlásení hráčov. Ručné pripomienkovanie a cielené úpravy zahŕňajú názvy predmetov a schopností, akcie, opisy, pokyny a ďalšie texty rozhrania; pri spracovaní opráv sa naďalej využíva aj AI.

**Celý preklad zatiaľ neprešiel úplnou ľudskou jazykovou a kontextovou revíziou.** Niektoré texty môžu byť nepresné, neprirodzené, nejednotné alebo zostať v angličtine. Verejné sprístupnenie neznamená, že ide o dokončený profesionálny preklad. Verzia **0.05 je testovacie vydanie**. Lokalizácia neposkytuje slovenský dabing a nemusí pokrývať texty dodávané serverom ani všetky obrázky s textom.

### Čo bolo otestované

Pri zostavení sa kontroluje zachovanie formátovacích značiek a zástupných hodnôt v textoch. Na oddelenej testovacej kópii herných súborov bola overená inštalácia prekladu 0.04 pre zostavu 3634150, online inštalácia a obnova pôvodnej angličtiny. Obnovené súbory sa pri teste zhodovali s originálmi po jednotlivých bajtoch.

Aktualizátor bol otestovaný aj s nesprávnym SHA-256, poškodeným balíkom, nepovoleným obsahom ZIPu, nekompatibilnou zostavou a simulovanou chybou počas zápisu. Overené bolo vrátenie predchádzajúceho stavu aj následná obnova prerušenej operácie. Po zverejnení sa overilo načítanie online manifestu a kontrolný súčet balíka stiahnutého z GitHubu.

Priebežné skúšanie v hre a hlásenia testerov pomáhajú odhaľovať chyby. Tieto kontroly však nie sú potvrdením, že boli prejdené všetky dialógy, úlohy, obrazovky a herné situácie. Najnovšie textové opravy môžu ešte vyžadovať vizuálne overenie v hre.

### Zálohy a bezpečná obnova

Pred prvou inštaláciou sa vytvára záloha pôvodných anglických súborov dotknutých lokalizáciou. Pri aktualizácii sa táto záloha neprepisuje slovenskými súbormi. Funkcia **Obnoviť angličtinu** používa pôvodné originály; nejde o zálohu uloženej hry ani celého herného priečinka.

Pred aktualizáciou sa navyše vytvára dočasná kópia aktuálneho stavu. Ak zápis zlyhá, aktualizátor sa pokúsi obnoviť predchádzajúcu verziu. Ak obnovu znemožní napríklad nedostupný disk alebo zamknutý súbor, potrebné dáta zostanú zachované a pri ďalšom spustení sa ponúkne obnova prerušenej operácie. Počas inštalácie, aktualizácie a obnovy musí byť hra ukončená.

Nové zálohy sa ukladajú do `%LOCALAPPDATA%\AniimoSlovencina\backups`. Podporované sú aj staršie zálohy v priečinku `Aniimo-SK-zaloha` pri hre. Zálohy nemaž ani neupravuj, pokiaľ ich chceš používať na obnovu. Ak sa herné súbory medzitým zmenili, inštalátor môže obnovu odmietnuť, aby starými súbormi neprepísal aktualizovanú hru.

### Kompatibilita a aktualizácie

Toto vydanie je pripravené pre zostavu ANIIMO **3634150**. Ide o označenie zostavy používané hrou, nie o Steam build ID. Kompatibilita s inými zostavami nie je potvrdená. Po aktualizácii hry môže byť potrebný upravený lokalizačný balík alebo nový kompatibilný inštalátor; samotná zmena čísla zostavy v manifeste nestačí.

Inštalátor overuje zostavu aj známe kontrolné súčty súborov. Pri nezhode alebo neznámych zmenách nemá súbory automaticky prepisovať. Súčasná kombinácia s inými úpravami rovnakých súborov nie je overená.

**Verzia prekladu a verzia inštalátora sú oddelené.** Online aktualizácie sťahujú iba lokalizačný balík, overujú jeho SHA-256 a povolený obsah. Samotné EXE sa automaticky neaktualizuje. Kontrolný súčet pomáha overiť neporušenosť balíka, nie jazykovú správnosť prekladu.

## Stiahnutie a inštalácia

[Stiahnuť inštalátor](https://github.com/XiuLe-cloud/aniimo-slovencina/releases/download/v0.04/Aniimo-Slovencina-Instalator-1.3-preklad-0.04.exe)

1. Ukonči ANIIMO a spusti inštalátor.
2. Skontroluj priečinok hry a nainštaluj slovenčinu.
3. Klikni na **Skontrolovať znova** a potom na **Aktualizovať na 0.05**. Pribalený preklad v EXE 1.3 je 0.04; najnovší preklad sa sťahuje online.
4. V hre ponechaj jazyk **English**.

Inštalátor uchová pôvodnú anglickú zálohu. Tlačidlo **Obnoviť angličtinu** obnoví originály.

Inštalátor **1.3** podporuje zostavu **3634150** a zachováva oranžovo-modrý vzhľad s tučniakom. Preklad **0.04** zahŕňa nové a zmenené texty; aj tieto texty sú priebežne revidovaný strojový návrh.

**Pri prechode z 1.2.1 alebo staršieho inštalátora si raz stiahni nové EXE 1.3.** Staré EXE má pevne určenú starú zostavu a názvy súborov, preto nový balík neprijme. Samotné EXE sa automaticky neaktualizuje.

Po spustení 1.3 klikni na **Skontrolovať znova** a potom na **Aktualizovať na 0.05**. Kontrola iba vyhľadá aktualizáciu; zápis začne až po stlačení tlačidla aktualizácie. Na čistej podporovanej hre sa ponúkne inštalácia.

Pri prechode po aktualizácii hry sa prijmú iba presne rozpoznané zvyšky pôvodných úprav a overené anglické originály. Záloha novej zostavy je uložená oddelene v `build-3634150`; stará záloha sa nemení. Neznáme úpravy sa neprepíšu.

Na oddelenej kópii zostavy 3634150 bol overený prechod zo zachovaných úprav 0.02 na 0.04, odmietnutie nesprávneho SHA-256, rollback po chybe zápisu a byte-identická obnova angličtiny novej zostavy. Herné testovanie nových textov ešte pokračuje.

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

Chyby a nesprávne preklady nám hlás prednostne na [Discorde Aniimo CZ/SK](https://discord.gg/ygN2cWJmRW). Po pripojení otvor fórum [chyby-prekladu](https://discord.com/channels/1546824435770720256/1554686019599859742). Alternatívne môžeš použiť [GitHub Issues](https://github.com/XiuLe-cloud/aniimo-slovencina/issues).

V hlásení uveď verziu prekladu, zostavu hry, miesto alebo situáciu, v ktorej sa chyba objavila, a prilož snímku nesprávneho textu. Ak môžeš, doplň pôvodný anglický text alebo návrh opravy. Pred odoslaním snímky skontroluj, či neobsahuje osobné údaje.

Ďakujeme všetkým hráčom, ktorí pomáhajú preklad skúšať a zlepšovať.

## Overenie vydania 0.04

Prešlo 31 testov pipeline. Technická kontrola 112 264 záznamov neobsahuje blokujúce chyby. Zahrnutý je 1 nový a 15 zmenených EN textov a cielené opravy starších chýb. Inštalačné testy overili odmietnutie nesprávneho SHA-256, rollback po chybe zápisu a bajtovo zhodnú obnovu angličtiny. Úplné jazykové a herné testovanie tohto vydania ešte neprebehlo.

## Aktualizácia prekladu 0.05

[Vydanie 0.05](https://github.com/XiuLe-cloud/aniimo-slovencina/releases/tag/v0.05) pridáva 1010 upravených záznamov: 934 opakovaných označení úrovne karavanu a 76 ďalších textov stôp, predmetov a rozhrania. Existujúci inštalátor **1.3 zostáva nezmenený**.

Prechod 0.04 → 0.05 bol overený na izolovanej kópii pomocou pôvodného aktualizátora, vrátane odmietnutia chybného SHA-256, rollbacku a byte-identickej obnovy angličtiny. Technická kontrola celého korpusu prešla bez blokujúcich chýb; úplná jazyková revízia ešte pokračuje.
