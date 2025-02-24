@echo off
setlocal ENABLEDELAYEDEXPANSION

set SHORTCUTPATH="%userprofile%\Desktop\run_guidance.url"
if exist "%userprofile%\Desktop" (
    del "%SHORTCUTPATH%"
    echo [InternetShortcut] >> "%SHORTCUTPATH%"
    echo URL="%CD%\run_guidance.bat" >> "%SHORTCUTPATH%"
    echo IconFile="%CD%\src\assets\favicon.ico" >> "%SHORTCUTPATH%"
    echo IconIndex=0 >> "%SHORTCUTPATH%"
)

set SHORTCUTPATH="%userprofile%\Onedrive\Desktop\run_guidance.url"
if exist "%userprofile%\Onedrive\Desktop" (
    del "%SHORTCUTPATH%"
    echo [InternetShortcut] >> "%SHORTCUTPATH%"
    echo URL="%CD%\run_guidance.bat" >> "%SHORTCUTPATH%"
    echo IconFile="%CD%\src\assets\favicon.ico" >> "%SHORTCUTPATH%"
    echo IconIndex=0 >> "%SHORTCUTPATH%"
)
