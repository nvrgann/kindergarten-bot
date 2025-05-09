import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
from config import TOKEN, CHAT_ID

VERSION = "v9.8"
bot = telebot.TeleBot(TOKEN)
log_buffer = []

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    full = f"[{VERSION}] {timestamp} — {msg}"
    print(full)
    log_buffer.append(full)

def send_logs():
    if log_buffer:
        bot.send_message(CHAT_ID, "\n".join(log_buffer[-30:]))

def switch_to_russian(driver, wait):
    log("Ожидание: кнопка языка (до 20 сек.)")
    try:
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Қазақ') or contains(text(),'Kaz')]")))
        btn.click()
        time.sleep(1)
        log("Язык переключён на русский")
        return True
    except Exception as e:
        log(f"Ошибка при ожидании 'кнопка языка': {type(e).__name__}")
        log("Ошибка при переключении языка")
        return False

def attempt_filter_combination(year, search_105):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        log("Страница открыта")
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
        wait = WebDriverWait(driver, 20)

        if not switch_to_russian(driver, wait):
            return

        time.sleep(1)
        log(f"Выбираем год {year}")
        try:
            year_input = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[2]")))
            year_input.click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(),'{year}')]"))).click()
        except Exception as e:
            log(f"Ошибка при выборе года: {type(e).__name__}")
            return

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
        rows = driver.find_elements(By.CLASS_NAME, "dx-row")

        found = []
        for r in rows:
            t = r.text.strip()
            if not t or "мест" not in t:
                continue
            if search_105 and "№105" in t:
                found.append(t)
            elif not search_105 and "№105" not in t:
                found.append(t)

        if found:
            prefix = "Найдено в 105:" if search_105 else "Найдены места:"
            for f in found:
                log(f"{prefix} {f}")
        else:
            log("Нет подходящих мест")

    except Exception as e:
        log(f"Глобальная ошибка: {type(e).__name__}")
    finally:
        driver.quit()

def main():
    log(f"{VERSION} bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")
    stages = [
        ("Гос + 2022 + №105", "2022", True),
        ("Гос + 2022 + all", "2022", False),
        ("Гос + 2020 + №105", "2020", True),
        ("Гос + 2020 + all", "2020", False),
    ]
    for label, year, only_105 in stages:
        log(f"Этап: {label}")
        attempt_filter_combination(year, only_105)

    send_logs()

if __name__ == "__main__":
    main()