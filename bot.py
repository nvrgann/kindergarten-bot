import time
import telebot
from datetime import datetime
from config import TOKEN, CHAT_ID
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

VERSION = "v9.12"

def send(text):
    now = datetime.now().strftime('%H:%M:%S')
    msg = f"[{VERSION}] {now} — {text}"
    print(msg)
    bot = telebot.TeleBot(TOKEN)
    bot.send_message(CHAT_ID, msg)

def open_site(driver):
    send("Открываем сайт...")
    driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "dx-datagrid")))

def select_combobox_value(wait, label_text, value_text):
    try:
        label = wait.until(EC.presence_of_element_located((
            By.XPATH, f"//label[contains(text(), '{label_text}')]/following-sibling::div//input")))
        label.click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-overlay-content")))
        time.sleep(1)
        item = wait.until(EC.element_to_be_clickable((
            By.XPATH, f"//div[contains(@class,'dx-item') and contains(text(), '{value_text}')]")))
        item.click()
        return True
    except Exception:
        return False

def find_rows(driver):
    time.sleep(2)
    return driver.find_elements(By.CLASS_NAME, "dx-row")

def check_kindergarten():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        wait = WebDriverWait(driver, 60)

        for year in ["2022", "2020"]:
            for target in ["№105", "all"]:
                send(f"Этап: Мемлекеттік + {year} + {target}")
                open_site(driver)

                if not select_combobox_value(wait, "Топтың жылы", year):
                    send(f"Ошибка: не удалось выбрать год {year}")
                    continue
                if not select_combobox_value(wait, "Балабақшаның түрі", "Мемлекеттік балабақша"):
                    send("Ошибка: не удалось выбрать тип ДДО")
                    continue

                rows = find_rows(driver)
                if not rows:
                    send("Таблица пуста")
                    continue

                found = []
                count_105 = 0
                for r in rows:
                    t = r.text.strip()
                    if not t or "орын" not in t:
                        continue
                    if "№105" in t:
                        count_105 += 1
                    else:
                        found.append(t)

                if target == "№105":
                    if count_105 > 0:
                        send(f"Найдено в 105 садике: {count_105} мест(а)")
                        return
                else:
                    if found:
                        send("В 105 садике мест нет. Зато есть:\n" + "\n".join(f"— {r}" for r in found))
                        return

    except Exception as e:
        send(f"Глобальная ошибка: {type(e).__name__} — {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    send(f"{VERSION} bot.py запущен — {datetime.now().strftime('%H:%M:%S')}")
    check_kindergarten()