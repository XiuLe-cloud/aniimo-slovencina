# Installer 1.5 / build 3732728 – technické overenie

CS 0.03-test.1; SK 0.09-test.1; 112 365 ID na jazyk.

14 integračných a 10 GUI kontrol PASS na izolovaných dátach. Živá hra nebola zmenená. Samostatné EXE bolo spustené mimo zdrojového projektu. Testované vo Windows PowerShell 5.1.

- PASS: CS update check is read-only
- PASS: Online signed SK installs from EN
- PASS: Online signed CS switches from SK
- PASS: Bundled SK switches from CS
- PASS: Restore English all12
- PASS: Online rollback error-first
- PASS: Online rollback exit-first
- PASS: Online rollback exit-state
- PASS: Reject signature even with matching feed hash
- PASS: Reject payload even with matching feed hash
- PASS: Reject traversal even with matching feed hash
- PASS: Reject wrong-language even with matching feed hash
- PASS: Wrong game build refused
- PASS: Steam and game protection retained
- PASS: Standalone EXE outside development directory detects isolated EN
- PASS: Local ZIP picker visible; install disabled before validation
- PASS: Signature-verified update version and path shown before installation
- PASS: Update screen 100/125/150/200% outer layout
- PASS: GUI confirmation includes game path/version/hash; imported CS installed
- PASS: Visible Restore English works after imported update
- PASS: Bundled CS is also latest 0.03-test.1
- PASS: Final GUI Restore English
- PASS: Bad new selection clears previous approved update
- PASS: No JavaScript errors

Kontroly zahŕňajú podpisy a obsah balíkov, nie osobné herné testovanie nového buildu. Reálne HTTPS sťahovanie oboch jazykov z GitHubu, podpis, inštalácia a následná obnova EN prešli ďalšími 6 kontrolami. Spolu 30 kontrol PASS. Úplná ručná revízia prekladov pokračuje.

SHA-256 EXE: `f4cf8e0c9ffb3267fe8534cc818f93cb8a5c8d568b09684d93f96012abf14ba8`.

- PASS: HTTPS sk channel check
- PASS: HTTPS signed sk install
- PASS: Restore English after HTTPS sk
- PASS: HTTPS cs channel check
- PASS: HTTPS signed cs install
- PASS: Restore English after HTTPS cs
