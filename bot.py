# kindergarten_bot v9.7

import time
from datetime import datetime
import telebot
from config import TOKEN, CHAT_ID
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

VERSION = "v9.7"

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{VERSION}] {timestamp} — {msg}"
    print(full_msg)
    try:
        bot = telebot.TeleBot(TOKEN)
        bot.send_message(CHAT_ID, full_msg)
    except Exception:
        pass

def switch_to_russian(wait, driver):
    try:
        log("Ожидание: кнопка языка (до 20 сек.)")
        btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(),'Қазақ') or contains(text(),'Kaz') or contains(text(),'KAZ')]")
        ))
        btn.click()
        time.sleep(1)
        log("Язык переключён на русский")
        return True
    except Exception as e:
        log(f"Ошибка при ожидании 'кнопка языка': {type(e).__name__}")
        log("Ошибка при переключении языка")
        return False

def select_ddo(wait, driver):
    try:
        comboboxes = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@role='combobox']")))
        if len(comboboxes) >= 6:
            comboboxes[5].click()
            wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(text(),'Государственный детский сад')]")
            )).click()
            return True
    except:
        pass
    log("Не удалось выбрать 'Государственный детский сад'")
    return False

def run_scenario(label):
    log(f"Этап: {label}")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    try:
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
        log("Страница открыта")
        time.sleep(2)
        if not switch_to_russian(wait, driver):
            return
        select_ddo(wait, driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    log(f"{VERSION} bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")
    for label in [
        "Гос + 2022 + №105",
        "Гос + 2022 + all",
        "Гос + 2020 + №105",
        "Гос + 2020 + all",
    ]:
        run_scenario(label)