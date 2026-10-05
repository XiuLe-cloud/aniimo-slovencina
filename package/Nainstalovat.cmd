@echo off
title Aniimo - instalacia slovenciny
echo ANIIMO - SLOVENSKY STROJOVY PREKLAD
echo Najprv ukonci hru. Instalator automaticky vyhlada Aniimo.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install.ps1"
if errorlevel 1 echo Instalacia sa nedokoncila. Precitaj si chybu vyssie.
pause
