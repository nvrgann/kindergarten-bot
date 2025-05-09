import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
from config import TOKEN, CHAT_ID

VERSION = "v9.10"
URL = "https://balabaqsha.open-almaty.kz/Common/Statistics/Free"

bot = telebot.TeleBot(TOKEN)
full_log = []

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{VERSION}] {timestamp} — {msg}"
    print(line)
    full_log.append(line)
    return line

def send(text, silent=True):
    bot.send_message(CHAT_ID, f"[{VERSION}] {text}", disable_notification=silent)

def send_log():
    if full_log:
        bot.send_message(CHAT_ID, "\n".join(full_log[-50:]))

def try_click_language(driver, wait):
    log("Ожидание: //a[contains(@href, '/ru')] (до 60 сек.)")
    try:
        lang_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/ru')]")))
        lang_button.click()
        time.sleep(1)
        log("Язык переключён на русский")
        return True
    except Exception as e:
        log(f"Ошибка при ожидании '//a[contains(@href, '/ru')]': {type(e).__name__}")
        return False

def open_site():
    log("Страница открыта")

def run_scenario(label):
    log(f"Этап: {label}")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(URL)
        open_site()
        wait = WebDriverWait(driver, 60)

        for attempt in range(3):
            success = try_click_language(driver, wait)
            if success:
                break
            else:
                log("Ошибка при переключении языка")
                driver.refresh()
                log("Страница открыта")
        else:
            log("Не удалось переключить язык после 3 попыток")

    finally:
        driver.quit()

def main():
    log(f"{VERSION} bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")
    run_scenario("Гос + 2022 + №105")
    run_scenario("Гос + 2022 + all")
    run_scenario("Гос + 2020 + №105")
    run_scenario("Гос + 2020 + all")
    send_log()

if __name__ == "__main__":
    main()