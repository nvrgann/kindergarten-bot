import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
from config import TOKEN, CHAT_ID

VERSION = "v9.11"
bot = telebot.TeleBot(TOKEN)
log_lines = []

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_message = f"[{VERSION}] {timestamp} — {message}"
    print(full_message)
    log_lines.append(full_message)

def send_log():
    text = "\n".join(log_lines)
    if text:
        bot.send_message(CHAT_ID, text[:4000])

def open_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def wait_for_language_switch(wait):
    try:
        log("Ожидание: кнопка языка (до 60 сек.)")
        button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/ru')]")))
        button.click()
        log("Язык переключён на русский")
        return True
    except Exception:
        log("Ошибка при ожидании '//a[contains(@href, '/ru')]': TimeoutException")
        log("Ошибка при переключении языка")
        return False

def select_filters(wait, driver):
    try:
        inputs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@role='combobox']")))
        if len(inputs) >= 6:
            # Тип ДДО — Мемлекеттік балабақша
            inputs[5].click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
            time.sleep(1)
            driver.find_element(By.XPATH, "//div[contains(text(),'Мемлекеттік балабақша')]").click()
            # Год — 2022
            inputs[1].click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
            time.sleep(1)
            driver.find_element(By.XPATH, "//div[contains(text(),'2022')]").click()
            return True
    except Exception:
        return False
    return False

def check_table(driver):
    try:
        rows = driver.find_elements(By.CLASS_NAME, "dx-row")
        if not rows:
            return "Ошибка: таблица не загрузилась или пуста."
        all_found = []
        priority_found = 0
        for row in rows:
            text = row.text.strip()
            if not text or "орын" not in text:
                continue
            if "№105" in text:
                priority_found += 1
            else:
                all_found.append(text)
        if priority_found > 0:
            return f"Найдено в 105 садике: {priority_found} орын(ы)"
        elif all_found:
            return "В 105 садике мест нет. Зато есть:\n" + "\n".join(f"— {r}" for r in all_found)
        else:
            return None
    except Exception as e:
        return f"Ошибка при чтении таблицы: {type(e).__name__}"

def run_bot():
    log(f"{VERSION} bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")
    for attempt in range(1, 4):
        log("Открываем сайт...")
        driver = open_driver()
        try:
            driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
            wait = WebDriverWait(driver, 60)
            log("Страница открыта")

            if not wait_for_language_switch(wait):
                driver.quit()
                continue

            if not select_filters(wait, driver):
                log("Не удалось выбрать фильтры")
                driver.quit()
                continue

            result = check_table(driver)
            if result:
                log(result)
            driver.quit()
            break
        except Exception as e:
            log(f"Глобальная ошибка: {type(e).__name__} — {str(e)}")
            driver.quit()
    send_log()

if __name__ == "__main__":
    run_bot()
