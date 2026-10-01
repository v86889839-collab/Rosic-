"""
Росич — фоновый режим (daemon)
Запускается при старте Windows, следит за .сфайл и логами.
Добавь в rosic.py обработку аргумента --daemon.

Логика:
1. Если в папке проекта есть .сфайл — останавливает циклы
2. Если есть новые .рос файлы во входящей папке — запускает их
3. Пишет лог в .лог файл
"""

import os
import sys
import time
import glob

DAEMON_INTERVAL = 30  # секунд между проверками
LOG_FILE = "rosic.лог"

def write_log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{ts}] {msg}\n")

def check_stop_files():
    """Проверяет наличие .сфайл"""
    stop_files = glob.glob("*.сфайл")
    if stop_files:
        write_log(f"Обнаружен стоп-файл: {stop_files}")
        return True
    return False

def main():
    write_log("Росич-демон запущен")
    
    while True:
        try:
            if check_stop_files():
                write_log("Стоп-файл активен — циклы отключены")
            else:
                # Здесь можно добавить логику запуска файлов
                pass
            
            time.sleep(DAEMON_INTERVAL)
        except KeyboardInterrupt:
            write_log("Росич-демон остановлен пользователем")
            break
        except Exception as e:
            write_log(f"Ошибка демона: {e}")
            time.sleep(DAEMON_INTERVAL)

if __name__ == "__main__":
    main()
