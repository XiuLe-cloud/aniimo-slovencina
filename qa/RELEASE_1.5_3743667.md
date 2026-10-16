# Installer 1.5 / ANIIMO build 3743667

CS 0.04-test.1, SK 0.10-test.1; 112 418 ID každý.

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
- PASS: Standalone EXE starts and detects isolated EN
- PASS: Embedded GUI served with correct build
- PASS: Standalone EXE bundled CS install
- PASS: Standalone EXE CS to SK switch
- PASS: Standalone EXE Restore English
- PASS: Standalone EXE validates signed local update
- PASS: Standalone EXE local update installation
- PASS: Standalone EXE final EN restoration

22 izolovaných integračných a EXE kontrol PASS. Navyše SHA-256 všetkých 8703 Lua položiek potvrdzuje zmenu iba dvoch lokalizačných súborov v každom jazyku. Prenos grafických úprav zachoval ostatné objekty nových assetov. Detekcia skutočnej Steam knižnice na D: overená read-only.

HTTPS testy verejných kanálov doplníme po publikovaní balíkov. Nebol vykonaný vizuálny ani osobný herný test nových textov. Žiadny test nezapisoval do živej hry.
