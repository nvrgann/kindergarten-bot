import os
import time
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot

from config import TOKEN, CHAT_ID

VERSION = 'v9.14'
URL = 'https://balabaqsha.open-almaty.kz/'

# Подготовка директорий
os.makedirs('logs', exist_ok=True)
os.makedirs('screens', exist_ok=True)

# Лог в файл и stdout
class Logger:
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("logs/log.txt", "w", encoding="utf-8")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger()

bot = telebot.TeleBot(TOKEN)

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{VERSION}] {timestamp} — {msg}")

def screenshot(driver, label):
    path = f"screens/{datetime.now().strftime('%H%M%S')}_{label}.png"
    driver.save_screenshot(path)
    with open(path, 'rb') as photo:
        bot.send_photo(CHAT_ID, photo)

def send_log_file():
    with open('logs/log.txt', 'rb') as f:
        bot.send_document(CHAT_ID, f)

def start_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def open_site(driver):
    for i in range(3):
        try:
            log("Открываем сайт...")
            driver.get(URL)
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dx-datagrid"))
            )
            log("Страница открыта")
            screenshot(driver, 'site')
            return True
        except Exception as e:
            log(f"Ошибка при открытии сайта: {e.__class__.__name__}")
            time.sleep(3)
    return False

def select_filter(driver, col_index, text, label):
    try:
        log(f"Фильтр [{label}] — ищем: '{text}'")
        filters = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'td.dx-command-select + td'))
        )
        filters[col_index].click()
        time.sleep(1)
        inputs = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.dx-overlay-wrapper input'))
        )
        inputs[0].send_keys(text)
        time.sleep(2)
        inputs[0].send_keys(u'\ue007')  # Enter
        log(f"Фильтр [{label}] применён: {text}")
        return True
    except Exception as e:
        log(f"Ошибка при фильтре [{label}]: {e.__class__.__name__}")
        screenshot(driver, f'error_{label}')
        return False

def run_stage(filter_year, filter_type, name=None):
    driver = start_driver()
    try:
        if not open_site(driver):
            return

        if not select_filter(driver, 1, filter_year, "Год"):
            log(f"Ошибка: не удалось выбрать год {filter_year}")
            return

        if not select_filter(driver, 5, filter_type, "Тип"):
            log(f"Ошибка: не удалось выбрать тип {filter_type}")
            return

        label = f"{filter_type} + {filter_year} + {name if name else 'all'}"
        log(f"Этап: {label}")

        if name:
            if not select_filter(driver, 0, name, "Название"):
                return

        time.sleep(5)
        rows = driver.find_elements(By.CSS_SELECTOR, 'div.dx-datagrid-rowsview tr')
        count = len(rows)
        if count > 0:
            log(f"Группы найдены: {count}")
            screenshot(driver, f'result_{label}')
        else:
            log("Группы отсутствуют")
            screenshot(driver, f'no_result_{label}')
    finally:
        driver.quit()

def main():
    log(f"{VERSION} bot.py запущен")
    stages = [
        ('2022', 'Мемлекеттік балабақша', '№105 бөбекжай-балабақшасы'),
        ('2022', 'Мемлекеттік балабақша', None),
        ('2020', 'Мемлекеттік балабақша', '№105 бөбекжай-балабақшасы'),
        ('2020', 'Мемлекеттік балабақша', None),
    ]
    for year, typ, name in stages:
        run_stage(year, typ, name)
    send_log_file()

if __name__ == '__main__':
    main()