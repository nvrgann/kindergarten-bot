import time
from datetime import datetime
import telebot
from config import TOKEN, CHAT_ID
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

VERSION = "v9.5"
bot = telebot.TeleBot(TOKEN)

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    full_msg = f"[{VERSION}] {timestamp} — {message}"
    print(full_msg)
    try:
        bot.send_message(CHAT_ID, full_msg)
    except:
        pass

def wait_for_element(driver, by, value, timeout=20, step=""):
    log(f"{step}Ожидание: {value} (до {timeout} сек.)")
    try:
        element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        return element
    except TimeoutException:
        log(f"{step}Ошибка при ожидании '{value}': TimeoutException")
        return None

def switch_to_russian(driver):
    lang_btn = wait_for_element(driver, By.XPATH, "//span[contains(text(),'Қазақ') or contains(text(),'Kaz')]", step="")
    if not lang_btn:
        log("Ошибка при переключении языка")
        return False
    try:
        lang_btn.click()
        time.sleep(1.5)
        ru_option = wait_for_element(driver, By.XPATH, "//div[contains(text(),'Рус') or contains(text(),'Rus')]", step="  ")
        if ru_option:
            ru_option.click()
            log("Язык переключён на русский")
            return True
    except Exception as e:
        log(f"Ошибка при переключении языка: {type(e).__name__}")
    log("Ошибка при переключении языка")
    return False

def select_type_ddo(driver):
    try:
        all_inputs = driver.find_elements(By.XPATH, "//input[@role='combobox']")
        if len(all_inputs) >= 6:
            all_inputs[5].click()
            time.sleep(1)
            option = wait_for_element(driver, By.XPATH, "//div[contains(text(),'Государственный детский сад')]", step="  ")
            if option:
                option.click()
                return True
    except Exception as e:
        log(f"Ошибка при выборе 'Государственный детский сад': {type(e).__name__}")
    log("Не удалось выбрать 'Государственный детский сад'")
    return False

def select_year(driver, year):
    try:
        year_input = driver.find_elements(By.XPATH, "//input[@role='combobox']")[1]
        year_input.click()
        time.sleep(1)
        option = driver.find_elements(By.XPATH, "//div[contains(@class, 'dx-item')]")
        found = False
        for el in option:
            if str(year) in el.text:
                el.click()
                found = True
                break
        if not found:
            log(f"Группы {year} года отсутствуют.")
            return False
        return True
    except Exception as e:
        log(f"Ошибка при выборе года {year}: {type(e).__name__}")
        return False

def check_rows(driver, target_105=True):
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
        rows = driver.find_elements(By.CLASS_NAME, "dx-row")
        matches = []
        for row in rows:
            txt = row.text.strip()
            if not txt or "мест" not in txt:
                continue
            if target_105 and "№105" in txt:
                matches.append(txt)
            elif not target_105 and "№105" not in txt:
                matches.append(txt)
        return matches
    except Exception as e:
        log(f"Ошибка при анализе строк таблицы: {type(e).__name__}")
        return []

def main_check(year, target_105):
    label = f"Гос + {year} + {'№105' if target_105 else 'all'}"
    log(f"Этап: {label}")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
        if not switch_to_russian(driver):
            driver.quit()
            return

        if not select_type_ddo(driver):
            driver.quit()
            return

        if not select_year(driver, year):
            driver.quit()
            return

        results = check_rows(driver, target_105)
        if results:
            for row in results:
                bot.send_message(CHAT_ID, f"[{VERSION}] Найдено: {row}", disable_notification=not target_105)
        else:
            log("Ничего не найдено")
    finally:
        driver.quit()

if __name__ == "__main__":
    log(f"{VERSION} bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")
    scenarios = [
        (2022, True),
        (2022, False),
        (2020, True),
        (2020, False),
    ]
    for year, is_105 in scenarios:
        main_check(year, is_105)