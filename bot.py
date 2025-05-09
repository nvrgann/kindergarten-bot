import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
from config import TOKEN, CHAT_ID

VERSION = "v8.9"
SILENT = True

bot = telebot.TeleBot(TOKEN)
log_messages = []

def log(msg, silent=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    full = f"[{VERSION}] {msg}" if not msg.startswith("[") else msg
    print(full)
    log_messages.append(full)
    if not silent or not SILENT:
        bot.send_message(CHAT_ID, full, disable_notification=silent)

def send_final_log():
    try:
        text = "\n".join(log_messages[-50:])
        bot.send_message(CHAT_ID, f"ДетСадБот (лог):\n{text}", disable_notification=True)
    except Exception as e:
        print(f"Ошибка при отправке лога: {e}")

def switch_to_russian(wait, driver):
    try:
        lang_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Рус')]")))
        lang_btn.click()
        wait.until(lambda d: "Рус" in d.find_element(By.CLASS_NAME, "language-button").text)
        log("Язык переключён на русский", silent=True)
        return True
    except Exception:
        log("Ошибка при переключении языка")
        return False

def select_type_ddo(wait, driver):
    try:
        inputs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@role='combobox']")))
        if len(inputs) < 6:
            raise Exception("Недостаточно полей combobox")
        inputs[5].click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Государственный детский сад')]"))).click()
        return True
    except Exception:
        log("Не удалось выбрать 'Государственный детский сад'")
        return False

def select_year(wait, driver, year):
    try:
        inputs = driver.find_elements(By.XPATH, "//input[@role='combobox']")
        inputs[1].click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
        options = driver.find_elements(By.XPATH, "//div[contains(@class,'dx-item')]")
        if not any(year in el.text for el in options):
            log(f"Группы {year} года отсутствуют.")
            return False
        driver.find_element(By.XPATH, f"//div[contains(text(),'{year}')]").click()
        return True
    except Exception:
        log(f"Ошибка при выборе года {year}")
        return False

def get_table_rows(wait, driver):
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
        return driver.find_elements(By.CLASS_NAME, "dx-row")
    except Exception:
        return []

def run_case(driver, wait, year, priority_only):
    if not switch_to_russian(wait, driver):
        return
    if not select_type_ddo(wait, driver):
        return
    if not select_year(wait, driver, year):
        return
    rows = get_table_rows(wait, driver)
    priority = [r.text.strip() for r in rows if "№105" in r.text and "мест" in r.text]
    others = [r.text.strip() for r in rows if "мест" in r.text and "№105" not in r.text]
    if priority_only:
        if priority:
            log(f"Найдено в 105 садике ({year}): {len(priority)} мест(а)")
        else:
            log(f"Нет мест в 105 садике ({year})")
    else:
        if others:
            msg = f"Места в других садиках ({year}):\n" + "\n".join(f"— {r}" for r in others)
            log(msg)
        else:
            log(f"Нет мест в других садиках ({year})")

def check_all():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 60)
    try:
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
        time.sleep(2)

        log(f"{VERSION} bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")
        log("Этап: Гос + 2022 + №105")
        run_case(driver, wait, "2022", priority_only=True)

        log("Этап: Гос + 2022 + all")
        run_case(driver, wait, "2022", priority_only=False)

        log("Этап: Гос + 2020 + №105")
        run_case(driver, wait, "2020", priority_only=True)

        log("Этап: Гос + 2020 + all")
        run_case(driver, wait, "2020", priority_only=False)

    finally:
        driver.quit()
        send_final_log()

if __name__ == "__main__":
    check_all()