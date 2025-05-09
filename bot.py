import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
from config import TOKEN, CHAT_ID

VERSION = "v8.5"
SILENT = True
ALWAYS_REPORT = True

log_text = ""

def log(text, silent=False):
    global log_text
    timestamp = f"[{VERSION}] {text}"
    print(timestamp)
    log_text += timestamp + "\n"

def send_log():
    if log_text.strip():
        try:
            bot = telebot.TeleBot(TOKEN)
            bot.send_message(CHAT_ID, log_text.strip(), disable_notification=SILENT)
        except Exception as e:
            print(f"[{VERSION}] Ошибка при отправке лога: {e}")

def wait_table_reload(wait):
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-loadpanel-message")))
        wait.until_not(EC.presence_of_element_located((By.CLASS_NAME, "dx-loadpanel-message")))
    except:
        pass

def select_language(driver, wait):
    try:
        lang_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'lang')]")))
        lang_text = lang_btn.text.strip().lower()
        log(f"Текущий язык: {lang_text}")
        if "қаз" in lang_text:
            log("Переключаем язык на русский")
            lang_btn.click()
            wait_table_reload(wait)
        else:
            log("Язык уже русский")
    except Exception as e:
        log("Ошибка при переключении языка")

def select_filter(wait, driver, index, value):
    try:
        inputs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@role='combobox']")))
        if index >= len(inputs):
            return False
        inputs[index].click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(),'{value}')]"))).click()
        wait_table_reload(wait)
        return True
    except Exception as e:
        log(f"Ошибка выбора фильтра '{value}': {type(e).__name__}")
        return False

def search_places(driver, keyword="№105"):
    rows = driver.find_elements(By.CLASS_NAME, "dx-row")
    results = []
    for row in rows:
        text = row.text.strip()
        if not text or "мест" not in text:
            continue
        if keyword in text or keyword == "любой":
            results.append(text)
    return results

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

def run_check():
    log(f"bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")
    results = []
    scenarios = [
        ("2022", "№105"),
        ("2022", "любой"),
        ("2020", "№105"),
        ("2020", "любой")
    ]

    try:
        for year, keyword in scenarios:
            driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
            wait = WebDriverWait(driver, 60)

            log(f"Этап: Гос + {year} + {keyword}")

            select_language(driver, wait)

            if not select_filter(wait, driver, 5, "Государственный детский сад"):
                results.append("Не удалось выбрать 'Государственный детский сад'")
                continue

            if not select_filter(wait, driver, 1, year):
                results.append(f"Год {year} отсутствует")
                continue

            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
            found = search_places(driver, keyword)

            if found:
                if keyword == "№105":
                    results.append(f"Найдено в №105 ({year}): {len(found)} мест")
                else:
                    results.append(f"Найдено ({year}):\n" + "\n".join(f"— {r}" for r in found))
                break

    except Exception as e:
        log(f"Глобальная ошибка: {type(e).__name__} — {str(e)}")

    finally:
        driver.quit()
        if results:
            for msg in results:
                log(msg)
        elif ALWAYS_REPORT:
            log("По всем сценариям ничего не найдено")
        send_log()

if __name__ == "__main__":
    run_check()