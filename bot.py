import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
from config import TOKEN, CHAT_ID

VERSION = "v8.8"
SILENT = True  # Если True, лог отправляется без звука. Если найдено место — со звуком.
log = []

def log_line(text):
    timestamp = time.strftime("%H:%M:%S")
    full_line = f"[{VERSION}] {text}"
    print(full_line)
    log.append(f"{full_line}")

def send_telegram(text, silent=True):
    bot = telebot.TeleBot(TOKEN)
    bot.send_message(CHAT_ID, text, disable_notification=silent)

def switch_to_russian(wait, driver):
    try:
        lang_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'lang') and contains(text(), 'Рус')]")))
        lang_button.click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-datagrid")))
        log_line("Язык переключён на русский")
        return True
    except Exception as e:
        log_line("Ошибка при переключении языка")
        return False

def select_ddo_type(wait, driver):
    try:
        inputs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@role='combobox']")))
        if len(inputs) >= 6:
            inputs[5].click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Государственный детский сад')]"))).click()
            return True
    except:
        return False
    return False

def select_year(wait, driver, year="2022"):
    try:
        inputs = driver.find_elements(By.XPATH, "//input[@role='combobox']")
        if len(inputs) >= 2:
            inputs[1].click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
            time.sleep(1)
            elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'dx-item')]")
            if any(year in el.text for el in elements):
                wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(),'{year}')]"))).click()
                return True
    except:
        pass
    return False

def read_table(driver):
    rows = driver.find_elements(By.CLASS_NAME, "dx-row")
    return [row.text.strip() for row in rows if row.text.strip() and "мест" in row.text]

def run_check(driver, wait, year, priority_only=False):
    if not switch_to_russian(wait, driver):
        return

    if not select_ddo_type(wait, driver):
        log_line("Не удалось выбрать 'Государственный детский сад'")
        return

    if not select_year(wait, driver, year):
        log_line(f"Группы {year} года отсутствуют.")
        return

    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
        results = read_table(driver)
        if not results:
            log_line("Свободных мест не найдено.")
            return
        if priority_only:
            filtered = [r for r in results if "№105" in r]
            if filtered:
                send_telegram(f"[{VERSION}] Найдено в 105 садике:\n" + "\n".join(filtered), silent=False)
            else:
                log_line("В 105 садике мест нет.")
        else:
            send_telegram(f"[{VERSION}] Найдены места:\n" + "\n".join(results), silent=False)
    except Exception as e:
        log_line(f"Ошибка при чтении таблицы: {type(e).__name__}")

def main():
    log_line(f"bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
        wait = WebDriverWait(driver, 60)

        log_line("Этап: Гос + 2022 + №105")
        run_check(driver, wait, "2022", priority_only=True)

        log_line("Этап: Гос + 2022 + all")
        run_check(driver, wait, "2022", priority_only=False)

        log_line("Этап: Гос + 2020 + №105")
        run_check(driver, wait, "2020", priority_only=True)

        log_line("Этап: Гос + 2020 + all")
        run_check(driver, wait, "2020", priority_only=False)

    except Exception as e:
        log_line(f"Глобальная ошибка: {type(e).__name__} — {str(e)}")

    finally:
        driver.quit()
        try:
            send_telegram("\n".join(log), silent=SILENT)
        except:
            pass

if __name__ == "__main__":
    main()