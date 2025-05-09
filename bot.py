import time
import telebot
from config import TOKEN, CHAT_ID
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

VERSION = "v7.5"
ALWAYS_REPORT = True
print(f"[{VERSION}] bot.py запущен")

def send_message(text):
    print(f"[{VERSION}] {text}")
    bot = telebot.TeleBot(TOKEN)
    bot.send_message(CHAT_ID, f"[{VERSION}] {text}")

def select_type_ddo(wait):
    print("Пробуем найти input с aria-label='Тип ДДО'")
    for attempt in range(2):
        try:
            input_ddo = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Тип ДДО']")))
            input_ddo.click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Государственный детский сад')]"))).click()
            print(f"Попытка {attempt+1}: успешно выбрали 'Государственный детский сад'")
            return True
        except Exception as e:
            print(f"Попытка {attempt+1} — ошибка при выборе типа ДДО: {type(e).__name__}")
            time.sleep(3)
    return False

def check_kindergarten():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
        wait = WebDriverWait(driver, 60)

        if not select_type_ddo(wait):
            return "Ошибка: фильтр 'Тип ДДО' не найден после 2 попыток."

        # Выбор года
        print("Выбираем год 2022")
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

        # Поиск садиков
        print("Читаем таблицу")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
        rows = driver.find_elements(By.CLASS_NAME, "dx-row")
        if not rows:
            return "Ошибка: таблица не загрузилась или пуста."

        # Сбор данных
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

if __name__ == "__main__":
    result = check_kindergarten()
    if result or ALWAYS_REPORT:
        send_message(result if result else "Проверка завершена. Свободных мест нет.")