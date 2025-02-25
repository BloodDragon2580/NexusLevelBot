@echo off
title NexusLevelBot Service Manager
cd /d C:\nssm\win64

:menu
cls
echo ================================
echo   NexusLevelBot Service Manager
echo ================================
echo [1] Starten des Dienstes
echo [2] Stoppen des Dienstes
echo [3] Dienst entfernen
echo [4] Beenden
echo ================================
set /p choice=Bitte waehle eine Option: 

if "%choice%"=="1" (
    echo Starte den NexusLevelBot-Dienst...
    nssm start NexusLevelBot
    pause
    goto menu
)

if "%choice%"=="2" (
    echo Stoppe den NexusLevelBot-Dienst...
    nssm stop NexusLevelBot
    pause
    goto menu
)

if "%choice%"=="3" (
    echo Entferne den NexusLevelBot-Dienst...
    nssm remove NexusLevelBot confirm
    pause
    goto menu
)

if "%choice%"=="4" (
    echo Beenden...
    exit
)

echo Ungueltige Eingabe. Bitte versuche es erneut.
pause
goto menu
