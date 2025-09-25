import time, whisper, os, requests, re #type:ignore
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By                # Locators (ID, CLASS_NAME, XPATH, etc.)
from selenium.webdriver.support.ui import WebDriverWait       # Waits for elements to appear
from selenium.webdriver.support import expected_conditions as EC  # Conditions like "visible", "clickable"
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

from app.constant import *
from app.captcha_solver import recognize_audio

def set_search_options(driver, wait, bench_index: int, appeal_index: int, date: str):
    try:
       #DROPDOWN BENCH
        bench_dropdown = wait.until(EC.visibility_of_element_located((By.ID, BENCH_SELECT)))
        bench_select = Select(bench_dropdown)

        # Validate index
        if bench_index >= len(bench_select.options):
            raise ValueError(f"Bench index {bench_index} out of range.")
        bench_select.select_by_index(bench_index)
        bench_name = bench_select.first_selected_option.text

        # DROPDOWN APPEAL
        appeal_dropdown = wait.until(EC.visibility_of_element_located((By.ID, APPLIC_SELECT)))
        driver.execute_script("arguments[0].scrollIntoView(true);", appeal_dropdown)
        appeal_select = Select(appeal_dropdown)

        if appeal_index >= len(appeal_select.options):
            raise ValueError(f"Appeal index {appeal_index} out of range.")
        appeal_select.select_by_index(appeal_index)
        appeal_name = appeal_select.first_selected_option.text

        # SET DATE
        order_date_input = wait.until(EC.visibility_of_element_located((By.ID, DATE_SELECT)))
        driver.execute_script("arguments[0].removeAttribute('readonly')", order_date_input)
        driver.execute_script("arguments[0].value = arguments[1];", order_date_input, date)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", order_date_input)

        print(f"Search options set: Bench='{bench_name}', Appeal='{appeal_name}', Date='{date}'")
        return bench_name, appeal_name, date

    except Exception as e:
        print(f"Failed to set search options: {e}")
        raise

def get_captcha_audio(driver):
    audio_btn = driver.find_element(By.XPATH, AUDIO_PLAY_BUTTON)
    driver.execute_script("arguments[0].scrollIntoView(true);", audio_btn)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", audio_btn)  # JS click avoids intercept
    time.sleep(2)
    return driver.find_element(By.ID, AUDIO_SOURCE).get_attribute("src")

def submit_captcha(captcha_text: str):
    captcha_input = driver.find_element(By.ID,CAPTCHA_ID)
    captcha_input.clear()
    print(f"Sending Text: {captcha_text}")
    captcha_input.send_keys(captcha_text)
    
    submit_btn = driver.find_element(By.ID, SUBMIT_CAPTCHA_BUTTON)
    driver.execute_script("arguments[0].click();", submit_btn)

def check_results_loaded(driver):
    try:
        wait = WebDriverWait(driver, 10)
        rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#results table tbody tr")))
        if rows:
            print(f"Results loaded with {len(rows)} row(s).")
            return True
        else:
            print("Results table found but no rows present.")
            return False
    except Exception as e:
        print(f"❌ Error checking results: {e}")
        return False

def scrape_results(driver, bench_name, appeal_name):
    """Scrape results table with pagination, return DataFrame or None"""
    print("Page Loaded.")
    wait = WebDriverWait(driver, 10)
    try:
        # Wait until either "No Records Found" OR at least one case row is visible
        wait.until(
            lambda d: (
                d.find_elements(By.CSS_SELECTOR, "#results table tbody tr td[colspan='5']")
                or d.find_elements(By.CSS_SELECTOR, "#results table tbody tr td:nth-child(2)")
            )
        )
    except Exception:
        print("Results table did not load.")
        return None

    no_data_cells = driver.find_elements(By.CSS_SELECTOR, "#results table tbody tr td[colspan='5']")
    if no_data_cells and "No Records Found" in no_data_cells[0].text:
        print("No records found. Skipping pagination.")
        return None

    # Figure out how many pages there are
    page_buttons = driver.find_elements(By.XPATH, PAGE_BTN_XPATH)
    max_pages = len(page_buttons) if page_buttons else 1
    print(f"Total Pages are {max_pages}.")

    data = []
    seen_links = set()

    for page_num in range(1, max_pages + 1):
        try:
            page_btn = driver.find_element(By.XPATH, f"//input[@name='btnPage' and @value='{page_num}']")
            driver.execute_script("arguments[0].scrollIntoView(true);", page_btn)

            if page_btn.get_attribute("disabled"):
                print(f"Skipping page {page_num} (already active).")
            else:
                # Click the page button (it's a submit input)
                driver.execute_script("arguments[0].click();", page_btn)
                print(f"-> Clicked page {page_num}")
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#results table tbody tr")))
                time.sleep(1.5)

            # Scrape table rows
            rows = driver.find_elements(By.CSS_SELECTOR, "#results table tbody tr")
            page_new_count = 0
            for row in rows:
                try:
                    parties = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text.strip()
                    order_link = row.find_element(
                        By.CSS_SELECTOR, "td:nth-child(4) a"
                    ).get_attribute("href")
                    if order_link and order_link not in seen_links:
                        seen_links.add(order_link)
                        data.append([bench_name, appeal_name, parties, order_link])
                        page_new_count += 1
                except Exception:
                    continue
            print(f"Rows on page {page_num}: {len(rows)} | new added: {page_new_count}")

        except Exception as e:
            print(f"⚠️ Failed to process page {page_num}: {e}")
            continue

    if data:
        df = pd.DataFrame(data, columns=["Bench", "Appeal", "Parties", "Order Link"])
        df["Order Link"] = df["Order Link"].apply(lambda url: f'=HYPERLINK("{url}", "{url}")')
        print(df.head(5))
        return data
    else:
        return None
    

def runner(driver, bench_index, appeal_index, dateTake):
    wait = WebDriverWait(driver, 15)
    MAX_ATTEMPTS = 5
    success = False
    attempt = 0
    print(f"Running for {bench_index}; {appeal_index}.")
    while attempt < MAX_ATTEMPTS and not success:
        
        if attempt == 0:
            driver.refresh()
        print(f"Attempt: {attempt + 1}")
        attempt += 1
        try:
            # 🔄 Ensure accordion tab is open
            accordion_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, HEADING_BUTTON)))
            driver.execute_script("arguments[0].click();", accordion_btn)
            time.sleep(1)

            bench_name, appeal_name, date_used = set_search_options(driver, wait, bench_index, appeal_index, dateTake)

            
            audio_url = get_captcha_audio(driver)
            data = recognize_audio(driver,audio_url)
            time.sleep(0.2)
            submit_captcha(data)

            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                print("Alert says:", alert.text)
                alert.accept()
                print("Retrying with new CAPTCHA...")
                driver.refresh()
                time.sleep(3)  # Let page reload
                continue  # Retry loop
            except TimeoutException:
                print("No alert — CAPTCHA accepted!")
                success = True
                time.sleep(0.5)
                break

        except Exception as e:
            print(f"❌ Failed during attempt {attempt}: {e}")
            time.sleep(.5)

    if success and check_results_loaded(driver):
        df = scrape_results(driver, bench_name, appeal_name)

        if isinstance(df, pd.DataFrame) and not df.empty:
            df.to_excel(f"{bench_name}_{appeal_name}.xlsx", index=False)
            print("Data saved.")
        else:
            print("No valid data to save or scraping failed.")

    else:
        print("No results found or CAPTCHA failed after max attempts.")


if __name__ == "__main__":
    
    bench_name = 20
    appeal_name = 1
    dates = "23/09/2025"
    
    
    options = Options()
    options.add_argument("--log-level=3")  # Suppress most logs
    driver = webdriver.Chrome(options=options)
    driver.get("https://itat.gov.in/judicial/tribunalorders")
    
    for appeal_name in range(1,19):
        runner(driver,bench_name,appeal_name,dates)
        print(f"==================Completed this Section.==================")
        driver.refresh()
    
    driver.quit()
    time.sleep(10)
    print("Driver has been quit.")
    