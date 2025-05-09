import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
from config import TOKEN, CHAT_ID

VERSION = "v8.6"
log = []

def log_step(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log.append(f"[{VERSION}] {message}")
    print(f"[{VERSION}] {message}")

def send_log_to_telegram(silent=False):
    bot = telebot.TeleBot(TOKEN)
    full_log = "\n".join(log)
    bot.send_message(CHAT_ID, full_log, disable_notification=silent)

def switch_language_to_russian(driver, wait):
    try:
        lang_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Рус')]")))
        lang_btn.click()
        WebDriverWait(driver, 10).until(EC.invisibility_of_element((By.CLASS_NAME, "dx-loadpanel-content")))
        log_step("Язык переключён на русский")
        return True
    except Exception:
        log_step("Ошибка при переключении языка")
        return False

def select_ddo_type(wait):
    try:
        input_box = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[6]")))
        input_box.click()
        WebDriverWait(input_box, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Государственный детский сад')]"))).click()
        return True
    except Exception:
        log_step("Не удалось выбрать 'Государственный детский сад'")
        return False

def select_group_year(wait, driver, year):
    try:
        input_box = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[2]")))
        input_box.click()
        time.sleep(1)
        options = driver.find_elements(By.XPATH, "//div[contains(@class,'dx-item')]")
        year_found = any(year in el.text for el in options)
        if not year_found:
            log_step(f"Группы {year} года отсутствуют.")
            return False
        wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(),'{year}')]"))).click()
        return True
    except Exception:
        log_step(f"Ошибка при выборе года {year}")
        return False

def parse_table(driver, wait, target="105"):
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
        rows = driver.find_elements(By.CLASS_NAME, "dx-row")
        results = [r.text for r in rows if r.text.strip() and "мест" in r.text]
        target_results = [r for r in results if target in r]
        if target_results:
            return f"Найдено в {target} садике:\n" + "\n".join(target_results), False
        elif results:
            return "В 105 садике мест нет. Найдено:\n" + "\n".join(results), False
        else:
            return "Мест нет вообще", True
    except Exception as e:
        return f"Ошибка при чтении таблицы: {type(e).__name__}", True

def main():
    log_step(f"bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        stages = [
            ("Гос", "2022", "№105"),
            ("Гос", "2022", "all"),
            ("Гос", "2020", "№105"),
            ("Гос", "2020", "all"),
        ]

        for stage in stages:
            ddo, year, target = stage
            log_step(f"Этап: {ddo} + {year} + {target}")

            driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
            wait = WebDriverWait(driver, 60)

            if not switch_language_to_russian(driver, wait):
                continue

            if not select_ddo_type(wait):
                continue

            if not select_group_year(wait, driver, year):
                continue

            result, is_empty = parse_table(driver, wait, "105" if target == "№105" else "")
            log_step(result)

    except Exception as e:
        log_step(f"Глобальная ошибка: {type(e).__name__} — {str(e)}")
    finally:
        driver.quit()
        send_log_to_telegram(silent=True)

if __name__ == "__main__":
    main()