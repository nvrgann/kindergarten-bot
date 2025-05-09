import time
from datetime import datetime
import telebot
from config import TOKEN, CHAT_ID
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib3.exceptions

VERSION = "v8.2"
ALWAYS_REPORT = True
VERBOSE = True
SILENT = True

log_lines = []
start_timestamp = datetime.now()
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def ignore_all_messages(message):
    pass  # молчание

def log(text):
    msg = f"[{VERSION}] {text}"
    print(msg)
    log_lines.append(msg)

def send_log():
    if VERBOSE and log_lines:
        try:
            bot.send_message(CHAT_ID, "\n".join(log_lines), disable_notification=SILENT)
        except Exception:
            pass

def send_result(text):
    silent = SILENT
    if "Найдено в 105" in text or "Зато есть:" in text:
        silent = False
    try:
        bot.send_message(CHAT_ID, f"[{VERSION}] {text}", disable_notification=silent)
    except Exception:
        pass

def try_select_ddo(wait, driver):
    try:
        input_ = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Тип ДДО']")))
        input_.click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
        time.sleep(1)
        driver.find_element(By.XPATH, "//div[contains(text(),'Государственный детский сад')]").click()
        log("Выбрано: Государственный детский сад")
        return True
    except Exception as e:
        log(f"Ошибка при выборе 'Государственный детский сад': {type(e).__name__}")
        return False

def check_kindergarten():
    start_time = time.time()
    log(f"bot.py запущен — {start_timestamp.strftime('%H:%M:%S')}")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        return f"Ошибка запуска Chrome: {type(e).__name__} — {str(e)}"

    def attempt():
        try:
            driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
            wait = WebDriverWait(driver, 60)
            log("Страница открыта")
            log(f"Первое действие: {datetime.now().strftime('%H:%M:%S')}")
            log("Шаг 1: выбор 'Тип ДДО'")
            return try_select_ddo(wait, driver)
        except Exception as e:
            log(f"Ошибка при загрузке страницы: {type(e).__name__}")
            return False

    try:
        if not attempt():
            log("Перезагружаем страницу и пробуем снова...")
            time.sleep(2)
            if not attempt():
                log("Повтор не помог. Переходим к поиску любых групп 2022 года.")

        wait = WebDriverWait(driver, 30)
        year_input = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[2]")))
        year_input.click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
        time.sleep(1)
        options = driver.find_elements(By.XPATH, "//div[contains(@class, 'dx-item')]")
        year_found = False
        for o in options:
            if "2022" in o.text:
                o.click()
                log("Выбрано: год 2022")
                year_found = True
                break
        if not year_found:
            return "Группы 2022 года отсутствуют."

        log("Шаг 3: анализ таблицы")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
        rows = driver.find_elements(By.CLASS_NAME, "dx-row")
        if not rows:
            return "Ошибка: таблица пуста."

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

        if priority_found:
            return f"Найдено в 105 садике: {priority_found} мест(а)"
        elif all_found:
            return "В 105 садике мест нет. Зато есть:\n" + "\n".join(f"— {r}" for r in all_found)
        else:
            return "Проверка завершена. Свободных мест нет."

    except (urllib3.exceptions.MaxRetryError, WebDriverException) as e:
        return f"Глобальная ошибка: {type(e).__name__} — {str(e)}"
    except Exception as e:
        return f"Непредвиденная ошибка: {type(e).__name__} — {str(e)}"
    finally:
        try:
            driver.quit()
        except:
            pass
        log(f"Выполнено за {round(time.time() - start_time, 2)} сек.")

if __name__ == "__main__":
    result = check_kindergarten()
    if result or ALWAYS_REPORT:
        log(result if result else "Проверка завершена.")
        send_result(result if result else "Проверка завершена.")
    send_log()