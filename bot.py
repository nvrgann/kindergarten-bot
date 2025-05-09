import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
from config import TOKEN, CHAT_ID

VERSION = "v9.6"

def log(message):
    now = datetime.now().strftime("%H:%M:%S")
    full = f"[{VERSION}] {now} — {message}"
    print(full)
    try:
        bot = telebot.TeleBot(TOKEN)
        bot.send_message(CHAT_ID, full)
    except:
        pass

def wait_for_element(driver, by, value, timeout=20, label=None):
    label_text = label or value
    log(f"Ожидание: {label_text} (до {timeout} сек.)")
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        return True
    except Exception as e:
        log(f"Ошибка при ожидании '{label_text}': {type(e).__name__}")
        return False

def switch_to_russian(driver):
    try:
        lang_button_xpath = "//span[contains(text(),'Қазақ') or contains(text(),'Kaz')]"
        if wait_for_element(driver, By.XPATH, lang_button_xpath, label="кнопка языка"):
            driver.find_element(By.XPATH, lang_button_xpath).click()
            log("Язык переключён на русский")
            return True
    except Exception:
        pass
    log("Ошибка при переключении языка")
    return False

def select_type_ddo(driver):
    try:
        wait = WebDriverWait(driver, 20)
        inputs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@role='combobox']")))
        if len(inputs) >= 6:
            type_input = inputs[5]
            type_input.click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Государственный детский сад')]"))).click()
            return True
    except Exception:
        pass
    log("Не удалось выбрать 'Государственный детский сад'")
    return False

def do_stage(driver, year, priority_only):
    label = f"Гос + {year} + {'№105' if priority_only else 'all'}"
    log(f"Этап: {label}")
    if not switch_to_russian(driver):
        return
    if not select_type_ddo(driver):
        return
    try:
        inputs = driver.find_elements(By.XPATH, "//input[@role='combobox']")
        if len(inputs) < 2:
            log("Не найден фильтр по году")
            return
        inputs[1].click()
        time.sleep(1)
        year_xpath = f"//div[contains(text(),'{year}')]"
        if wait_for_element(driver, By.XPATH, year_xpath, label=f"год {year}"):
            driver.find_element(By.XPATH, year_xpath).click()
        else:
            log(f"Год {year} отсутствует в списке")
            return
    except Exception:
        log("Ошибка при выборе года")

    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
        rows = driver.find_elements(By.CLASS_NAME, "dx-row")
        found = []
        for row in rows:
            text = row.text.strip()
            if "мест" in text:
                if priority_only and "№105" in text:
                    found.append(text)
                elif not priority_only and "№105" not in text:
                    found.append(text)
        if found:
            log("Найдено:\n" + "\n".join(found))
        else:
            log("Ничего не найдено")
    except Exception:
        log("Ошибка при чтении таблицы")

def run_bot():
    log(f"{VERSION} bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
    try:
        for year in [2022, 2020]:
            for priority in [True, False]:
                do_stage(driver, year, priority)
    finally:
        driver.quit()

if __name__ == "__main__":
    run_bot()