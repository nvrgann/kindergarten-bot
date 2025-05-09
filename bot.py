import time
from datetime import datetime
import telebot
from config import TOKEN, CHAT_ID
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

VERSION = "v8.0"
ALWAYS_REPORT = True
VERBOSE = True
SILENT = True  # лог без звука, результат — зависит от текста

log_lines = []
start_timestamp = datetime.now()

def log(text):
    message = f"[{VERSION}] {text}"
    print(message)
    log_lines.append(message)

def send_log():
    if VERBOSE and log_lines:
        bot = telebot.TeleBot(TOKEN)
        bot.send_message(CHAT_ID, "\n".join(log_lines), disable_notification=SILENT)

def send_result(text):
    silent = SILENT
    if "Найдено в 105" in text or "Зато есть:" in text:
        silent = False
    bot = telebot.TeleBot(TOKEN)
    bot.send_message(CHAT_ID, f"[{VERSION}] {text}", disable_notification=silent)

def find_ddo_by_label_text(wait, driver, label_text, option_text):
    try:
        log(f"Ищем фильтр по тексту: '{label_text}'")
        label = wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{label_text}')]")))
        container = label.find_element(By.XPATH, "./ancestor::div[contains(@class, 'dx-field')]")
        combobox = container.find_element(By.XPATH, ".//input[@role='combobox']")
        combobox.click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
        time.sleep(0.5)
        option = driver.find_element(By.XPATH, f"//div[contains(text(), '{option_text}')]")
        option.click()
        log(f"Выбрано: {option_text}")
        return True
    except Exception as e:
        log(f"Ошибка при выборе фильтра '{label_text}': {type(e).__name__}")
        return False

def check_kindergarten():
    script_started = time.time()
    log(f"bot.py запущен — {start_timestamp.strftime('%H:%M:%S')}")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
        wait = WebDriverWait(driver, 60)
        log("Страница открыта")

        first_action_time = datetime.now()
        log(f"Первое действие: {first_action_time.strftime('%H:%M:%S')}")

        log("Шаг 1: Поиск фильтра 'Тип ДДО' по тексту")
        if not find_ddo_by_label_text(wait, driver, "Тип ДДО", "Государственный детский сад"):
            return "Ошибка: не удалось выбрать 'Государственный детский сад' по тексту"

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
        duration = round(time.time() - script_started, 2)
        log(f"Выполнено за {duration} сек.")

if __name__ == "__main__":
    result = check_kindergarten()
    if result or ALWAYS_REPORT:
        log(result if result else "Проверка завершена. Свободных мест нет.")
        send_result(result if result else "Проверка завершена.")
    send_log()