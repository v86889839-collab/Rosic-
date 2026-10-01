@echo off
setlocal

REM Путь к python — можно оставить просто python, если он в PATH
set PY=python

REM Если файл передан как аргумент — запускаем его
if not [%1]==[] (
    %PY% rosic.py %1
) else (
    echo Использование: перетащи .рос или .test файл на rosic.bat
    echo Или запусти: rosic.bat main.рос
    pause
)
