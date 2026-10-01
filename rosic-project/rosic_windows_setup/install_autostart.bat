@echo off
chcp 65001 >nul 2>&1
setlocal

REM ============================================
REM  Росич — установка в автозагрузку
REM  Запусти этот файл от имени администратора
REM ============================================

set ROSIC_DIR=%~dp0
set AUTOSTART=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

REM Создаём ярлык через PowerShell
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%AUTOSTART%\Росич.lnk'); $sc.TargetPath = 'pythonw.exe'; $sc.Arguments = '\"%ROSIC_DIR%rosic.py\" --daemon'; $sc.WorkingDirectory = '%ROSIC_DIR%'; $sc.Description = 'Росич — фоновый режим'; $sc.Save()"

echo ============================================
echo   Росич добавлен в автозагрузку!
echo   Путь: %AUTOSTART%\Росич.lnk
echo ============================================
echo.
echo   Для удаления:
echo   Удали файл "Росич.lnk" из папки автозагрузки
echo   (Win+R -> shell:startup)
echo.
pause
