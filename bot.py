import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
from config import TOKEN, CHAT_ID

VERSION = "v8.3"
SILENT = True
ALWAYS_REPORT = True

def send(text, silent=False):
    print(f"[{VERSION}] {text}")
    try:
        bot = telebot.TeleBot(TOKEN)
        bot.send_message(CHAT_ID, f"[{VERSION}] {text}", disable_notification=(silent and SILENT))
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

def log_step(title):
    send(title)

def search_places(wait, driver, keyword="№105"):
    rows = driver.find_elements(By.CLASS_NAME, "dx-row")
    results = []
    for row in rows:
        text = row.text.strip()
        if not text or "мест" not in text:
            continue
        if keyword in text:
            results.append(text)
    return results

def select_filter(wait, index, value):
    try:
        inputs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@role='combobox']")))
        if index >= len(inputs):
            return False
        inputs[index].click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
        time.sleep(1)
        driver.find_element(By.XPATH, f"//div[contains(text(),'{value}')]").click()
        return True
    except:
        return False

def try_search(year, keyword="№105"):
    try:
        log_step(f"Этап: Гос + {year} + {keyword if keyword != 'любой' else 'все'}")
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
        wait = WebDriverWait(driver, 30)

        if not select_filter(wait, 5, "Государственный детский сад"):
            return f"Не удалось выбрать 'Государственный детский сад'"

        if not select_filter(wait, 1, year):
            return f"Год {year} отсутствует"

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
        time.sleep(1)
        if keyword == "любой":
            results = search_places(wait, driver, "")
        else:
            results = search_places(wait, driver, keyword)

        if results:
            if keyword == "№105":
                return f"Найдено в №105 ({year}): {len(results)} мест"
            else:
                return f"Найдено ({year}):\n" + "\n".join(f"— {r}" for r in results)
        return None
    except Exception as e:
        return f"Ошибка поиска: {type(e).__name__} — {str(e)}"

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

def run_check():
    send(f"bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")
    results = []

    scenarios = [
        ("2022", "№105"),
        ("2022", "любой"),
        ("2020", "№105"),
        ("2020", "любой")
    ]

    for year, keyword in scenarios:
        result = try_search(year, keyword)
        if result:
            results.append(result)
            if "№105" in result or "Найдено" in result:
                break

    driver.quit()
    if results:
        for msg in results:
            send(msg, silent=not ("№105" in msg or "Найдено" in msg))
    elif ALWAYS_REPORT:
        send("По всем сценариям ничего не найдено", silent=True)

if __name__ == "__main__":
    run_check()