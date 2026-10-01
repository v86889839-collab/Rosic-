@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM ============================================
REM  Росич — прогон всех .test файлов
REM  Положи в папку tests/ и запусти
REM ============================================

set PY=python
set ROSIC=%~dp0..\rosic.py
set TESTS=%~dp0

set PASS=0
set FAIL=0

echo ============================================
echo   РОСИЧ — МАССИВНЫЙ ТЕСТ
echo ============================================
echo.

for %%f in ("%TESTS%*.test") do (
    echo Запуск: %%~nxf
    %PY% "%ROSIC%" "%%f"
    if !errorlevel! equ 0 (
        set /a PASS+=1
    ) else (
        set /a FAIL+=1
    )
    echo.
)

echo ============================================
echo   ИТОГ: !PASS! прошли, !FAIL! упали
echo ============================================
pause
