import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telebot
from config import TOKEN, CHAT_ID

VERSION = "v9.3"
bot = telebot.TeleBot(TOKEN)

def now():
    return datetime.now().strftime('%H:%M:%S')

def log(text):
    msg = f"[{VERSION}] {now()} — {text}"
    print(msg)
    try:
        bot.send_message(CHAT_ID, msg)
    except:
        pass

def wait_for_element(wait, description, condition, timeout=20):
    log(f"Ожидание: {description} (до {timeout} сек.)")
    try:
        element = WebDriverWait(wait._driver, timeout).until(condition)
        log(f"Ожидание завершено: {description}")
        return element
    except Exception as e:
        log(f"Ошибка при ожидании '{description}': {type(e).__name__}")
        return None

def switch_to_russian(wait):
    lang_btn = wait_for_element(wait, "кнопка языка", EC.element_to_be_clickable((By.CLASS_NAME, "lang")))
    if lang_btn:
        lang_btn.click()
        time.sleep(0.5)
        ru_btn = wait_for_element(wait, "русский язык", EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Рус')]")))
        if ru_btn:
            ru_btn.click()
            log("Язык переключён на русский")
            return True
    log("Ошибка при переключении языка")
    return False

def select_ddo(wait):
    try:
        comboboxes = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@role='combobox']")))
        if len(comboboxes) >= 6:
            comboboxes[5].click()
            option = wait_for_element(wait, "'Государственный детский сад'", EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Государственный детский сад')]")))
            if option:
                option.click()
                return True
    except Exception as e:
        log(f"Не удалось выбрать 'Государственный детский сад': {type(e).__name__}")
    log("Не удалось выбрать 'Государственный детский сад'")
    return False

def select_year(wait, year):
    try:
        year_input = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@role='combobox'])[2]")))
        year_input.click()
        time.sleep(1)
        options = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'dx-item')]")))
        year_found = any(year in opt.text for opt in options)
        if not year_found:
            log(f"Группы {year} года отсутствуют")
            return False
        for opt in options:
            if year in opt.text:
                opt.click()
                return True
    except Exception as e:
        log(f"Ошибка при выборе года {year}: {type(e).__name__}")
    return False

def read_table(driver, wait, priority="105"):
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dx-row")))
    rows = driver.find_elements(By.CLASS_NAME, "dx-row")
    found = []
    for row in rows:
        text = row.text.strip()
        if "мест" in text:
            found.append(text)
    if not found:
        log("Нет доступных мест")
        return
    priority_rows = [r for r in found if priority in r]
    if priority_rows:
        log(f"Найдено в садике №{priority}:\n" + "\n".join(priority_rows))
    else:
        log("В приоритетном садике мест нет. Зато есть:\n" + "\n".join(found))

def run_stage(driver, wait, year, mode):
    log(f"Этап: Гос + {year} + {mode}")
    if not switch_to_russian(wait):
        return
    if not select_ddo(wait):
        return
    if not select_year(wait, year):
        return
    read_table(driver, wait, priority="105" if mode == "№105" else "")

def main():
    log(f"{VERSION} bot.py запущен — {now()}")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
    wait = WebDriverWait(driver, 60)

    try:
        for year in ["2022", "2020"]:
            for mode in ["№105", "all"]:
                run_stage(driver, wait, year, mode)
    except Exception as e:
        log(f"Глобальная ошибка: {type(e).__name__} — {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()