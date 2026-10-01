# Росич — Установка на Windows

## Что внутри

| Файл | Что делает |
|------|-----------|
| `rosic.bat` | Запуск по двойному клику + drag-and-drop |
| `install_associations.reg` | Привязка .рос, .rus, .функц, .test, .сфайл к Росичу |
| `uninstall_associations.reg` | Откат привязок |
| `install_context_menu.reg` | Пункт "Запустить Росич" в правом клике |
| `uninstall_context_menu.reg` | Откат контекстного меню |
| `install_autostart.bat` | Добавить Росич в автозагрузку |
| `uninstall_autostart.bat` | Убрать из автозагрузки |
| `build_exe.bat` | Собрать Rosic.exe (без Python на целевом ПК) |
| `run_tests_all.bat` | Прогнать все .test файлы разом |
| `rosic_daemon.py` | Фоновый режим (мониторинг .сфайл) |
| `install_all.py` | Мастер — делает всё сразу |

## Быстрый старт (вариант 1 — ручной)

1. Положи `rosic.bat` рядом с `rosic.py`
2. Перетащи любой `.рос` файл на `rosic.bat`
3. Готово

## Полная установка (вариант 2 — автоматический)

```
python install_all.py
```
Скрипт спросит, что установить, найдёт Python и rosic.py,
пропишет пути в .reg файлы и запустит их.

## Сборка EXE (вариант 3 — без Python)

```
build_exe.bat
```
Создаст `dist\Rosic.exe`. Можно копировать на любой ПК.

## Откат

- Ассоциации: `uninstall_associations.reg`
- Контекстное меню: `uninstall_context_menu.reg`
- Автозагрузка: `uninstall_autostart.bat`
