import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot

from config import TOKEN, CHAT_ID

bot = telebot.TeleBot(TOKEN)

VERSION = 'v9.13'
URL = 'https://balabaqsha.open-almaty.kz/'

# Папка логов и скриншотов
os.makedirs('logs', exist_ok=True)
os.makedirs('screens', exist_ok=True)

log_file = open('logs/log.txt', 'w', encoding='utf-8')


def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{VERSION}] {timestamp} — {msg}"
    print(line)
    log_file.write(line + '\n')
    log_file.flush()
    bot.send_message(CHAT_ID, line, disable_notification=True)


def screenshot(driver, label):
    path = f"screens/{datetime.now().strftime('%H%M%S')}_{label}.png"
    driver.save_screenshot(path)
    with open(path, 'rb') as photo:
        bot.send_photo(CHAT_ID, photo)


def send_log_file():
    log_file.close()
    with open('logs/log.txt', 'rb') as f:
        bot.send_document(CHAT_ID, f)


def start_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)


def open_site(driver):
    log("Открываем сайт...")
    driver.get(URL)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "dx-datagrid")))
    log("Страница открыта")
    screenshot(driver, 'site')


def select_filter(driver, col_index, text, label):
    try:
        log(f"Фильтр [{label}] — ищем: '{text}'")
        filters = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'td.dx-command-select + td'))
        )
        filters[col_index].click()
        time.sleep(1)

        items = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.dx-overlay-wrapper input'))
        )
        items[0].send_keys(text)
        time.sleep(2)
        items[0].send_keys(u'\ue007')  # Enter

        log(f"Фильтр [{label}] применён: {text}")
        return True
    except Exception as e:
        log(f"Ошибка при фильтре [{label}]: {e.__class__.__name__}")
        screenshot(driver, f'error_{label}')
        return False


def run_stage(filter_year, filter_type, name=None):
    driver = start_driver()
    try:
        open_site(driver)

        if not select_filter(driver, 1, filter_year, "Год"):
            log(f"Ошибка: не удалось выбрать год {filter_year}")
            return

        if not select_filter(driver, 5, filter_type, "Тип"):
            log(f"Ошибка: не удалось выбрать тип {filter_type}")
            return

        if name:
            success = select_filter(driver, 0, name, "Название")
            label = f"{filter_type} + {filter_year} + {name}"
        else:
            success = True
            label = f"{filter_type} + {filter_year} + all"

        log(f"Этап: {label}")

        if success:
            # Ждём загрузку данных
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