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

        # Ожидание загрузки фильтров
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dx-page-size"))
        )

        # Выбор "100 записей на страницу"
        driver.find_element(By.CLASS_NAME, "dx-page-size").click()
        driver.find_element(By.XPATH, "//div[contains(text(),'100')]").click()

        # Выбор фильтра "Год группы"
        time.sleep(2)
        driver.find_elements(By.CLASS_NAME, "dx-texteditor-input")[1].click()
        driver.find_element(By.XPATH, "//div[contains(text(),'2022')]").click()

        # Выбор фильтра "Тип ДДО"
        time.sleep(1)
        driver.find_elements(By.CLASS_NAME, "dx-texteditor-input")[5].click()
        driver.find_element(By.XPATH, "//div[contains(text(),'Государственный детский сад')]").click()

        # Ждём появления строк таблицы
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dx-row"))
        )

        # Считаем количество нужных строк
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