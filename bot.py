import time
import telebot
from config import TOKEN, CHAT_ID
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def send_message(text):
    bot = telebot.TeleBot(TOKEN)
    bot.send_message(CHAT_ID, text)

def check_kindergarten():
    send_message("Шаг 1: Запуск браузера и переход на сайт")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
        wait = WebDriverWait(driver, 30)

        send_message("Шаг 2: Установка фильтра '100 записей'")
        page_size_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "dx-page-size")))
        page_size_button.click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'100')]"))).click()

        send_message("Шаг 3: Выбор года группы = 2022")
        year_input = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[2]")))
        year_input.click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'2022')]"))).click()

        send_message("Шаг 4: Выбор типа ДДО = Государственный детский сад")
        type_input = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[6]")))
        type_input.click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
        wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Государственный детский сад')]"))).click()

        send_message("Шаг 5: Чтение таблицы")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
        rows = driver.find_elements(By.CLASS_NAME, "dx-row")
        count = sum(1 for row in rows if "№105" in row.text)

        return count

    except Exception as e:
        return f"Ошибка на этапе: {str(e)}"
    finally:
        driver.quit()

if __name__ == "__main__":
    result = check_kindergarten()
    if isinstance(result, int):
        if result > 0:
            send_message(f"Найдено в 105 садике: {result} мест(а)")
        else:
            send_message("В 105 садике мест нет.")
    else:
        send_message(result)