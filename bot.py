import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
from config import TOKEN, CHAT_ID

VERSION = "v9.9"
URL = "https://balabaqsha.open-almaty.kz/Common/Statistics/Free"

bot = telebot.TeleBot(TOKEN)

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{VERSION}] {timestamp} — {msg}"
    print(full_msg)
    try:
        bot.send_message(CHAT_ID, full_msg)
    except:
        pass

def wait_and_click_xpath(driver, xpath, timeout=60):
    try:
        log(f"Ожидание: {xpath} (до {timeout} сек.)")
        elem = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        elem.click()
        return True
    except Exception as e:
        log(f"Ошибка при ожидании '{xpath}': {type(e).__name__}")
        return False

def switch_to_russian(driver):
    try:
        # Проверка: уже русский?
        if "ru" in driver.current_url:
            log("Русский язык уже включён")
            return True
        return wait_and_click_xpath(driver, "//a[contains(@href, '/ru')]", 60)
    except Exception as e:
        log(f"Ошибка при переключении языка: {type(e).__name__}")
        return False

def run_check():
    log(f"{VERSION} bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)

    try:
        for year in [2022, 2020]:
            for priority in ["№105", "all"]:
                log(f"Этап: Гос + {year} + {priority}")
                driver.get(URL)
                time.sleep(3)
                log("Страница открыта")
                if not switch_to_russian(driver):
                    log("Ошибка при переключении языка")
                    continue
                # Остальная логика фильтрации и проверки здесь (пока опущена)
                # ...
                time.sleep(1)
    except Exception as e:
        log(f"Глобальная ошибка: {type(e).__name__} — {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_check()