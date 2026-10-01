@echo off
chcp 65001 >nul 2>&1
setlocal

set AUTOSTART=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

if exist "%AUTOSTART%\Росич.lnk" (
    del "%AUTOSTART%\Росич.lnk"
    echo Росич удалён из автозагрузки.
) else (
    echo Росич не найден в автозагрузке.
)
pause
