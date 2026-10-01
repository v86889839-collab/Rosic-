@echo off
chcp 65001 >nul 2>&1
setlocal

REM ============================================
REM  Росич — сборка в .exe
REM  Требуется: pip install pyinstaller
REM ============================================

echo Установка PyInstaller...
pip install pyinstaller

echo.
echo Сборка Rosic.exe...
pyinstaller --onefile --name Rosic --console --clean rosic.py

echo.
echo ============================================
echo   Готово! Файл: dist\Rosic.exe
echo ============================================
echo.
echo   Теперь можно:
echo   1. Запускать Rosic.exe main.рос
echo   2. Перетаскивать .рос файлы на Rosic.exe
echo   3. Копировать Rosic.exe на любой ПК
echo      (Python не нужен!)
echo.
pause
