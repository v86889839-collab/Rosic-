"""
Росич — Мастер установки для Windows
Запусти: python install_all.py
Скрипт спросит путь к Python и rosic.py, потом настроит всё автоматически.
"""

import os
import sys
import subprocess
from pathlib import Path

def get_python_path():
    py = sys.executable
    print(f"Python найден: {py}")
    return py

def find_rosic_py():
    candidates = [
        Path(__file__).parent / "rosic.py",
        Path.cwd() / "rosic.py",
        Path(__file__).parent.parent / "rosic.py",
    ]
    for c in candidates:
        if c.exists():
            print(f"rosic.py найден: {c}")
            return str(c.resolve())
    
    manual = input("Введите путь к rosic.py: ").strip('"')
    if os.path.isfile(manual):
        return os.path.abspath(manual)
    print("rosic.py не найден!")
    sys.exit(1)

def patch_reg(reg_path, py_path, rosic_path):
    """Заменяет C:\Path\To\ на реальные пути"""
    with open(reg_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace(r"C:\Path\To\python.exe", py_path)
    content = content.replace(r"C:\Path\To\rosic.py", rosic_path)
    patched = reg_path.replace(".reg", ".patched.reg")
    with open(patched, "w", encoding="utf-8") as f:
        f.write(content)
    return patched

def main():
    print("=" * 50)
    print("  РОСИЧ — Мастер установки для Windows")
    print("=" * 50)
    print()

    py_path = get_python_path()
    rosic_path = find_rosic_py()
    rosic_dir = os.path.dirname(rosic_path)

    print()
    print("Что установить?")
    print("  1. Ассоциации файлов (.рос, .rus, .функц, .test, .сфайл)")
    print("  2. Контекстное меню (правый клик → Запустить Росич)")
    print("  3. Автозагрузку (фоновый режим при старте Windows)")
    print("  4. ВСЁ СРАЗУ")
    print("  0. Выход")
    print()

    choice = input("Выбор: ").strip()

    if choice in ("1", "4"):
        print("\n[1/3] Ассоциации файлов...")
        reg = os.path.join(os.path.dirname(__file__), "install_associations.reg")
        patched = patch_reg(reg, py_path, rosic_path)
        subprocess.run(["reg", "import", patched], shell=True)
        print("  ✓ Ассоциации установлены")

    if choice in ("2", "4"):
        print("\n[2/3] Контекстное меню...")
        reg = os.path.join(os.path.dirname(__file__), "install_context_menu.reg")
        patched = patch_reg(reg, py_path, rosic_path)
        subprocess.run(["reg", "import", patched], shell=True)
        print("  ✓ Контекстное меню добавлено")

    if choice in ("3", "4"):
        print("\n[3/3] Автозагрузка...")
        bat = os.path.join(os.path.dirname(__file__), "install_autostart.bat")
        subprocess.run(["cmd", "/c", bat], shell=True)
        print("  ✓ Автозагрузка настроена")

    print("\n" + "=" * 50)
    print("  Установка завершена!")
    print("=" * 50)
    print()
    print("Теперь можно:")
    print(f"  — Двойной клик по .рос → запуск Росича")
    print(f"  — Правый клик по папке → 'Запустить Росич здесь'")
    print(f"  — Перетащить файл на rosic.bat")
    print()
    print("Для отката запусти uninstall_associations.reg")
    print("               и uninstall_context_menu.reg")
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()
