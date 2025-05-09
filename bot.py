import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
from config import TOKEN, CHAT_ID

VERSION = "v9.0"
SILENT = True

bot = telebot.TeleBot(TOKEN)
log = []

def log_msg(text):
    timestamp = datetime.now().strftime('%H:%M:%S')
    entry = f"[{VERSION}] {text}"
    print(entry)
    log.append(f"{timestamp} — {text}")

def send_log():
    message = "\n".join(f"[{VERSION}] {line}" for line in log)
    bot.send_message(CHAT_ID, message, disable_notification=SILENT)

def send_alert(text):
    bot.send_message(CHAT_ID, f"[{VERSION}] {text}", disable_notification=False)

def try_switch_language(driver, wait):
    try:
        lang_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Рус')]")))
        lang_button.click()
        WebDriverWait(driver, 10).until(EC.staleness_of(lang_button))
        log_msg("Язык переключён на русский")
        return True
    except Exception as e:
        log_msg("Ошибка при переключении языка")
        return False

def try_select_type(wait, driver):
    try:
        type_input = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[6]")))
        type_input.click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Государственный детский сад')]"))).click()
        return True
    except:
        log_msg("Не удалось выбрать 'Государственный детский сад'")
        return False

def try_select_year(wait, driver, year):
    try:
        year_input = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[2]")))
        year_input.click()
        time.sleep(1)
        options = driver.find_elements(By.XPATH, "//div[contains(@class, 'dx-item')]")
        if any(year in el.text for el in options):
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(),'{year}')]"))).click()
            return True
        else:
            log_msg(f"Группы {year} года отсутствуют")
            return False
    except:
        log_msg("Ошибка при выборе года")
        return False

def scan_table(driver):
    try:
        rows = driver.find_elements(By.CLASS_NAME, "dx-row")
        return [r.text for r in rows if "мест" in r.text]
    except:
        log_msg("Ошибка при чтении таблицы")
        return []

def run_check(label, year, look_for_105=True):
    log_msg(f"Этап: {label}")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
        wait = WebDriverWait(driver, 30)

        try_switch_language(driver, wait)
        if not try_select_type(wait, driver):
            return
        if not try_select_year(wait, driver, year):
            return
        results = scan_table(driver)
        if not results:
            log_msg("Нет данных в таблице")
        elif look_for_105:
            matches = [r for r in results if "№105" in r]
            if matches:
                send_alert(f"Найдено в 105 садике: {len(matches)} мест(а)")
            else:
                log_msg("В 105 садике мест нет")
        else:
            msg = "\n".join(f"— {r}" for r in results)
            send_alert(f"Найдены места ({label}):\n{msg}")
    finally:
        driver.quit()

if __name__ == "__main__":
    log_msg(f"{VERSION} bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")
    run_check("Гос + 2022 + №105", "2022", look_for_105=True)
    run_check("Гос + 2022 + all", "2022", look_for_105=False)
    run_check("Гос + 2020 + №105", "2020", look_for_105=True)
    run_check("Гос + 2020 + all", "2020", look_for_105=False)
    send_log()