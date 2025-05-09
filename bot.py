import time
import telebot
from config import TOKEN, CHAT_ID
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def check_kindergarten():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")

        try:
            page_size_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "dx-page-size")))
            page_size_button.click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'100')]"))).click()
        except Exception as e:
            return f"Ошибка на шаге: выбор количества строк — {e}"

        try:
            year_input = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[2]")))
            year_input.click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'2022')]"))).click()
        except Exception as e:
            return f"Ошибка на шаге: выбор фильтра 'Год группы' — {e}"

        try:
            type_input = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[6]")))
            type_input.click()
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Государственный детский сад')]"))).click()
        except Exception as e:
            return f"Ошибка на шаге: выбор фильтра 'Тип ДДО' — {e}"

        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
            rows = driver.find_elements(By.CLASS_NAME, "dx-row")
            count = sum(1 for row in rows if "№105" in row.text)
            return count
        except Exception as e:
            return f"Ошибка на шаге: чтение таблицы — {e}"

    except Exception as e:
        return f"Ошибка общая: {e}"
    finally:
        driver.quit()

def send_message(text):
    bot = telebot.TeleBot(TOKEN)
    bot.send_message(CHAT_ID, text)

if __name__ == "__main__":
    result = check_kindergarten()
    if isinstance(result, int):
        if result > 0:
            send_message(f"Найдено в 105 садике: {result} мест(а)")
    else:
        send_message(result)
