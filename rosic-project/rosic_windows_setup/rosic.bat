@echo off
chcp 65001 >nul 2>&1
setlocal

REM ============================================
REM  Росич — запускатель для Windows
REM  Положи этот файл рядом с rosic.py
REM ============================================

REM Путь к Python (если в PATH — просто "python")
set PY=python

REM Путь к интерпретатору
set ROSIC=%~dp0rosic.py

REM Если передан файл — запускаем его
if not [%1]==[] (
    %PY% "%ROSIC%" %1
    echo.
    echo ============================================
    echo  Росич завершил работу. Нажмите любую клавишу.
    echo ============================================
    pause >nul
) else (
    echo ============================================
    echo   РОСИЧ — язык программирования
    echo ============================================
    echo.
    echo   Использование:
    echo     rosic.bat main.рос        — запустить файл
    echo     rosic.bat tests/test.test — запустить тесты
    echo.
    echo   Или перетащи .рос / .test файл на этот .bat
    echo.
    echo   Запуск интерактивного режима (REPL):
    echo     rosic.bat --repl
    echo.
    if /i "%1"=="--repl" (
        %PY% "%ROSIC%"
    ) else (
        echo   Для выхода нажмите любую клавишу.
        pause >nul
    )
)
