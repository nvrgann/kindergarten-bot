import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
from config import TOKEN, CHAT_ID

VERSION = "v8.7"
bot = telebot.TeleBot(TOKEN)
log = []

def log_step(message):
    entry = f"[{VERSION}] {message}"
    print(entry)
    log.append(entry)

def send_log():
    bot.send_message(CHAT_ID, "\n".join(log))

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def switch_to_russian(driver, wait):
    try:
        lang_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class,'lang') and text()='ҚАЗ']")))
        lang_button.click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'РУС')]")))
        log_step("Язык переключён на русский")
        return True
    except Exception as e:
        log_step("Ошибка при переключении языка")
        return False

def try_select_type_ddo(wait):
    try:
        input_box = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[6]")))
        input_box.click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Государственный детский сад')]"))).click()
        return True
    except:
        log_step("Не удалось выбрать 'Государственный детский сад'")
        return False

def run_stage(label, year=None, find_105=False):
    log_step(f"Этап: {label}")
    driver = setup_driver()
    try:
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
        wait = WebDriverWait(driver, 60)

        if not switch_to_russian(driver, wait):
            return

        if not try_select_type_ddo(wait):
            return

        if year:
            try:
                year_input = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[2]")))
                year_input.click()
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
                time.sleep(1)
                options_list = driver.find_elements(By.XPATH, "//div[contains(@class, 'dx-item')]")
                if any(str(year) in el.text for el in options_list):
                    wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(),'{year}')]"))).click()
                else:
                    log_step(f"Группы {year} года отсутствуют.")
                    return
            except Exception as e:
                log_step(f"Ошибка при выборе года {year}")
                return

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
        rows = driver.find_elements(By.CLASS_NAME, "dx-row")
        found_105 = 0
        other = []

        for row in rows:
            text = row.text.strip()
            if "мест" not in text:
                continue
            if "№105" in text:
                found_105 += 1
            else:
                other.append(text)

        if find_105 and found_105 > 0:
            log_step(f"Найдено в 105 садике: {found_105} мест")
        elif find_105:
            log_step("В 105 садике мест нет.")
        elif other:
            log_step("Есть места:\n" + "\n".join(f"— {r}" for r in other))
        else:
            log_step("Нет мест.")
    except Exception as e:
        log_step(f"Глобальная ошибка: {type(e).__name__} — {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    log_step(f"bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")
    run_stage("Гос + 2022 + №105", year=2022, find_105=True)
    run_stage("Гос + 2022 + all", year=2022)
    run_stage("Гос + 2020 + №105", year=2020, find_105=True)
    run_stage("Гос + 2020 + all", year=2020)
    send_log()