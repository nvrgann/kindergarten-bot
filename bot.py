import time
from datetime import datetime
import telebot
from config import TOKEN, CHAT_ID
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

VERSION = "v7.7"
ALWAYS_REPORT = True
VERBOSE = True

log_lines = []

def log(text):
    message = f"[{VERSION}] {text}"
    print(message)
    log_lines.append(message)

def send_log():
    if VERBOSE and log_lines:
        bot = telebot.TeleBot(TOKEN)
        bot.send_message(CHAT_ID, "\n".join(log_lines))

def send_message(text):
    bot = telebot.TeleBot(TOKEN)
    bot.send_message(CHAT_ID, f"[{VERSION}] {text}")

def find_combobox_with_option(wait, driver, target_text):
    inputs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@role='combobox']")))
    for i, combobox in enumerate(inputs):
        try:
            combobox.click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
            time.sleep(0.5)
            options = driver.find_elements(By.XPATH, "//div[contains(@class,'dx-item')]")
            for option in options:
                if target_text in option.text:
                    option.click()
                    return True
        except Exception:
            continue
    return False

def check_kindergarten():
    start_time = time.time()
    log("bot.py запущен")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
        wait = WebDriverWait(driver, 60)

        log("Шаг 1: Поиск и выбор фильтра 'Тип ДДО'")
        if not find_combobox_with_option(wait, driver, "Государственный детский сад"):
            return "Ошибка: не удалось найти и выбрать 'Государственный детский сад'"

        log("Шаг 2: Выбор года = 2022")
        try:
            year_input = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[2]")))
            year_input.click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
            time.sleep(1)
            options_list = driver.find_elements(By.XPATH, "//div[contains(@class, 'dx-item')]")
            year_2022_exists = any("2022" in el.text for el in options_list)
            if not year_2022_exists:
                return "Группы 2022 года отсутствуют для выбранного фильтра."
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'2022')]"))).click()
        except Exception as e:
            return f"Ошибка при выборе года: {type(e).__name__} — {str(e)}"

        log("Шаг 3: Проверка таблицы")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
        rows = driver.find_elements(By.CLASS_NAME, "dx-row")
        if not rows:
            return "Ошибка: таблица не загрузилась или пуста."

        all_found = []
        priority_found = 0
        for row in rows:
            text = row.text.strip()
            if not text or "мест" not in text:
                continue
            if "№105" in text:
                priority_found += 1
            else:
                all_found.append(text)

        if priority_found > 0:
            return f"Найдено в 105 садике: {priority_found} мест(а)"
        elif all_found:
            return "В 105 садике мест нет. Зато есть:\n" + "\n".join(f"— {r}" for r in all_found)
        else:
            return "Проверка завершена. Свободных мест нет."

    except Exception as e:
        return f"Глобальная ошибка: {type(e).__name__} — {str(e)}"
    finally:
        driver.quit()
        duration = round(time.time() - start_time, 2)
        log(f"Выполнено за {duration} сек.")

if __name__ == "__main__":
    result = check_kindergarten()
    if result or ALWAYS_REPORT:
        log(result if result else "Проверка завершена. Свободных мест нет.")
    send_log()