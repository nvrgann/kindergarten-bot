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

    try:
        driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
        wait = WebDriverWait(driver, 20)

        # Ожидаем кнопку "100 строк на странице"
        page_size_button = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "dx-page-size"))
        )
        page_size_button.click()

        # Ожидаем появление пункта "100"
        option_100 = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'100')]"))
        )
        option_100.click()

        # Фильтр "Год группы" (вторая строка фильтра)
        year_filter_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[2]"))
        )
        year_filter_input.click()

        # Ждём появление пункта "2022"
        year_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'2022')]"))
        )
        year_option.click()

        # Фильтр "Тип ДДО" (шестая строка фильтра)
        type_filter_input = wait.until(
            EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[6]"))
        )
        type_filter_input.click()

        # Ждём "Государственный детский сад"
        type_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Государственный детский сад')]"))
        )
        type_option.click()

        # Ждём загрузку строк таблицы
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "dx-row"))
        )

        # Считаем строки с "№105"
        rows = driver.find_elements(By.CLASS_NAME, "dx-row")
        count = sum(1 for row in rows if "№105" in row.text)
        return count

    except Exception as e:
        return f"Ошибка: {e}"
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
