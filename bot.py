import time
import telebot
import traceback
from config import TOKEN, CHAT_ID
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

VERSION = "v7.2"

def send_message(text):
    bot = telebot.TeleBot(TOKEN)
    bot.send_message(CHAT_ID, f"[{VERSION}] {text}")

def check_kindergarten():
    send_message("Шаг 1: запуск и открытие сайта")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
        wait = WebDriverWait(driver, 30)

        # Шаг 2: выбор типа ДДО
        send_message("Шаг 2: Выбор типа ДДО = Государственный детский сад")
        try:
            type_input = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[6]")))
            type_input.click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Государственный детский сад')]"))).click()
            time.sleep(1)
        except Exception as e:
            return f"Ошибка при выборе типа ДДО: {type(e).__name__} — {str(e)}"

        # Шаг 3: проверка наличия года 2022
        send_message("Шаг 3: Проверка наличия группы 2022 года")
        try:
            year_input = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[2]")))
            year_input.click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
            time.sleep(1)
            options = driver.find_elements(By.XPATH, "//div[contains(@class, 'dx-item')]")
            year_2022_exists = any("2022" in el.text for el in options)

            if not year_2022_exists:
                send_message("Группы 2022 года отсутствуют для выбранного фильтра.")
                return 0

            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'2022')]"))).click()
        except Exception as e:
            return f"Ошибка при выборе года: {type(e).__name__} — {str(e)}"

        # Шаг 4: поиск строк
        send_message("Шаг 4: Проверка таблицы")
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
            rows = driver.find_elements(By.CLASS_NAME, "dx-row")
            count = sum(1 for row in rows if "№105" in row.text)
            return count
        except Exception as e:
            return f"Ошибка при чтении таблицы: {type(e).__name__} — {str(e)}"

    except Exception as e:
        return f"Глобальная ошибка: {type(e).__name__} — {str(e)}"
    finally:
        driver.quit()

if __name__ == "__main__":
    result = check_kindergarten()
    if isinstance(result, int):
        if result > 0:
            send_message(f"Найдено в 105 садике: {result} мест(а)")
        elif result == 0:
            pass
        else:
            send_message("В 105 садике мест нет.")
    else:
        send_message(result)