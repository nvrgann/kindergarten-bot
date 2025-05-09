import time from datetime import datetime from selenium import webdriver from selenium.webdriver.chrome.options import Options from selenium.webdriver.common.by import By from selenium.webdriver.support.ui import WebDriverWait from selenium.webdriver.support import expected_conditions as EC import telebot from config import TOKEN, CHAT_ID

VERSION = "v8.7" log = []

def log_line(text): stamp = f"[{VERSION}] {text}" print(stamp) log.append(stamp)

def send_log(): if log: bot = telebot.TeleBot(TOKEN) bot.send_message(CHAT_ID, "\n".join(log), disable_notification=True)

def send_message(text, silent=False): bot = telebot.TeleBot(TOKEN) bot.send_message(CHAT_ID, f"[{VERSION}] {text}", disable_notification=silent)

def switch_to_russian(wait, driver): try: lang_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Рус')]"))) lang_btn.click() WebDriverWait(driver, 10).until_not(EC.presence_of_element_located((By.CLASS_NAME, "dx-loadpanel-content"))) log_line("Язык переключён на русский") return True except: log_line("Ошибка при переключении языка") return False

def select_ddo_type(wait, driver): try: inputs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//input[@role='combobox']"))) for inp in inputs: if "Тип ДДО" in inp.get_attribute("aria-label"): inp.click() time.sleep(1) wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Государственный детский сад')]"))).click() return True return False except: return False

def select_year(wait, driver, year): try: inputs = driver.find_elements(By.XPATH, "//input[@role='combobox']") if len(inputs) >= 2: inputs[1].click() time.sleep(1) options = driver.find_elements(By.XPATH, f"//div[contains(text(),'{year}')]") if options: options[0].click() return True return False except: return False

def search_rows(driver): try: rows = driver.find_elements(By.CLASS_NAME, "dx-row") return [r.text.strip() for r in rows if "мест" in r.text] except: return []

def stage_check(driver, wait, year, search_105_only): if not switch_to_russian(wait, driver): return if not select_ddo_type(wait, driver): log_line("Не удалось выбрать 'Государственный детский сад'") return if not select_year(wait, driver, year): log_line(f"Группы {year} года отсутствуют.") return rows = search_rows(driver) if not rows: log_line("Нет результатов в таблице") return if search_105_only: found = [r for r in rows if "№105" in r] if found: for r in found: log_line(f"Найдено в 105: {r}") else: log_line("В 105 садике мест нет") else: for r in rows: log_line(f"Найдено: {r}")

def main(): log_line(f"bot.py запущен — {datetime.now().strftime('%H:%M:%S')}") options = Options() options.add_argument('--headless') options.add_argument('--no-sandbox') options.add_argument('--disable-dev-shm-usage') driver = webdriver.Chrome(options=options) driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free") wait = WebDriverWait(driver, 30)

stages = [
    ("Гос + 2022 + №105", 2022, True),
    ("Гос + 2022 + all", 2022, False),
    ("Гос + 2020 + №105", 2020, True),
    ("Гос + 2020 + all", 2020, False),
]

for label, year, only105 in stages:
    log_line(f"Этап: {label}")
    driver.get("https://balabaqsha.open-almaty.kz/Common/Statistics/Free")
    time.sleep(2)
    stage_check(driver, wait, year, only105)

driver.quit()
send_log()

if name == "main": try: main() except Exception as e: log_line(f"Глобальная ошибка: {type(e).name} — {e}") send_log()

