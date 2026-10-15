# Installer 1.5 – oprava premenovaného EXE (test.2)

Opravuje falošné hlásenie „Najskôr ukonči ANIIMO aj Steam“, keď prehliadač uloží súbor napríklad ako `ANIIMO-Localization-Installer-1.5 (4).exe`. Vlastný proces sa teraz identifikuje overeným rodičovským PID, nie názvom súboru. Ochrana pred spustenou hrou a Steamom zostáva zachovaná.

**Stiahni nový EXE, zavri starý Installer a spusti opravený.** Súbor môže mať aj iný názov. Ak už preklad funguje, netreba ho len kvôli tejto oprave preinštalovať.

CS 0.03-test.1, SK 0.09-test.1, build 3732728 a 112 365 ID na jazyk zostávajú nezmenené. Online aktualizácie oboch jazykov zostávajú zapnuté. ZIPy sú voliteľné a totožné s test.1; na použitie stačí EXE. Oprava programu sa cez jazykový kanál nedoručuje, preto treba tento EXE stiahnuť ručne.

Overenie: 8 regresných kontrol ochrany procesov a 2 read-only testy finálneho EXE s rôznymi názvami PASS. Predchádzajúcich 30 kontrol jazykových balíkov zostáva zdokumentovaných pri test.1; všetky sa pri tomto hotfixe neopakovali. Do živej hry sa nezapisovalo.

Neoficiálny komunitný preklad od Xiu_Le, testovacie vydanie. EXE nie je podpísané certifikátom Windows; SHA-256 je priložené. Aktualizačné ZIPy majú overovaný kryptografický podpis. Distribúcia naďalej obsahuje herné fontové a úvodné assety vrátane resources.assets.resS; práva k hernému obsahu zostávajú vlastníkom.

SHA-256 EXE: `73a36397a66eb21c54c4ff66c1ac84c4134aeefec39c88f6747e11befdef4bb1`

- PASS: Own PID exempt: ANIIMO-Localization-Installer-1.5.exe
- PASS: Own PID exempt: ANIIMO-Localization-Installer-1.5 (4).exe
- PASS: Own PID exempt: Aniimo moj installer.exe
- PASS: Other process blocked: Aniimo.exe
- PASS: Other process blocked: Aniimo-Win64-Shipping.exe
- PASS: Other process blocked: ANIIMO-Localization-Installer-1.5.exe
- PASS: Actual parent accepted; zero grants no exemption; forged parent rejected
- PASS: Both production guards use verified host identity; Steam guard retained
- PASS: ANIIMO-Localization-Installer-1.5 (4).exe
- PASS: Moj premenovany installer.exe
