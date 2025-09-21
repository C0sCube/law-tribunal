import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from app.constant import *


class TribunalScraper:
    def __init__(self, url: str, headless=False):
        self.url = url
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--disable-features=PlatformTelemetry")
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_position(0, 0)
        self.driver.set_window_size(WINDOW_HEIGHT, WINDOW_WIDTH)
        self.wait = WebDriverWait(self.driver, DEFAULT_WAIT)

    def start(self):
        self.driver.get(self.url)

    def set_search_options(self, bench_index: int, appeal_index: int, date: str):
        # 🔄 Wait for accordion to reappear after reload
        accordion_btn = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, HEADING_BUTTON))
        )
        self.driver.execute_script("arguments[0].click();", accordion_btn)
        time.sleep(1)

        # ✅ Now wait for Bench dropdown to exist
        bench_dropdown = self.wait.until(
            EC.presence_of_element_located((By.ID, BENCH_SELECT))
        )
        bench_select = Select(bench_dropdown)
        bench_select.select_by_index(bench_index)
        bench_name = bench_select.first_selected_option.text

        # ✅ Same for Appeal
        appeal_dropdown = self.wait.until(
            EC.presence_of_element_located((By.ID, APPLIC_SELECT))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", appeal_dropdown)
        appeal_select = Select(appeal_dropdown)
        appeal_select.select_by_index(appeal_index)
        appeal_name = appeal_select.first_selected_option.text

        # ✅ Set date safely
        order_date_input = self.wait.until(
            EC.presence_of_element_located((By.ID, DATE_SELECT))
        )
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", order_date_input)
        self.driver.execute_script("arguments[0].value = arguments[1];", order_date_input, date)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", order_date_input)

        return bench_name, appeal_name

    
    def get_captcha_audio(self):
        audio_btn = self.driver.find_element(By.XPATH, AUDIO_PLAY_BUTTON)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", audio_btn)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", audio_btn)  # JS click avoids intercept
        time.sleep(2)
        return self.driver.find_element(By.ID, AUDIO_SOURCE).get_attribute("src")


    def submit_captcha(self, captcha_text: str):
        captcha_input = self.driver.find_element(By.ID, "captcha")
        captcha_input.clear()
        #UpperCase the captcha text
        captcha_text = captcha_text.upper()
        for char in captcha_text:
            captcha_input.send_keys(char)
            time.sleep(0.1)
        submit_btn = self.driver.find_element(By.ID, SUBMIT_CAPTCHA_BUTTON)
        self.driver.execute_script("arguments[0].click();", submit_btn)

    def scrape_results(self, bench_name, appeal_name, ui=None):
        """Scrape results table with pagination, return DataFrame or None"""
        print("Page Loaded.")
        try:
            # Wait until either "No Records Found" OR at least one case row is visible
            self.wait.until(
                lambda d: (
                    d.find_elements(By.CSS_SELECTOR, "#results table tbody tr td[colspan='5']")
                    or d.find_elements(By.CSS_SELECTOR, "#results table tbody tr td:nth-child(2)")
                )
            )
        except Exception:
            if ui: ui.log("⚠️ Results table did not load.")
            return None

        if ui: ui.log("==================== results present =====================")
        # print("==================== results present =====================")

        # Check for "No Records Found"
        no_data_cells = self.driver.find_elements(
            By.CSS_SELECTOR, "#results table tbody tr td[colspan='5']"
        )
        if no_data_cells and "No Records Found" in no_data_cells[0].text:
            if ui: ui.log("No records found. Skipping pagination.")
            return None

        # Figure out how many pages there are
        page_buttons = self.driver.find_elements(By.XPATH, "//input[@name='btnPage']")
        max_pages = len(page_buttons) if page_buttons else 1
        if ui: ui.log(f"Total Pages are {max_pages}.")

        data = []
        seen_links = set()

        for page_num in range(1, max_pages + 1):
            try:
                page_btn = self.driver.find_element(
                    By.XPATH, f"//input[@name='btnPage' and @value='{page_num}']"
                )

                # Skip disabled button (current page)
                if page_btn.get_attribute("disabled"):
                    if ui: ui.log(f"Skipping page {page_num} (already active).")
                else:
                    # Click the page button (it's a submit input)
                    self.driver.execute_script("arguments[0].click();", page_btn)
                    if ui: ui.log(f"➡️ Clicked page {page_num}")

                    # Wait for table to refresh
                    self.wait.until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#results table tbody tr"))
                    )
                    time.sleep(1.5)  # extra buffer for stability

                # Scrape table rows
                rows = self.driver.find_elements(By.CSS_SELECTOR, "#results table tbody tr")
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
                if ui: ui.log(f"   Rows on page {page_num}: {len(rows)} | new added: {page_new_count}")

            except Exception as e:
                if ui: ui.log(f"⚠️ Failed to process page {page_num}: {e}")
                continue

        if data:
            df = pd.DataFrame(data, columns=["Bench", "Appeal", "Parties", "Order Link"])
            df["Order Link"] = df["Order Link"].apply(
                lambda url: f'=HYPERLINK("{url}", "{url}")'
            )
            return df
        else:
            return None

    def reset_form(self):
        try:
            accordion_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, HEADING_BUTTON))
            )
            self.driver.execute_script("arguments[0].click();", accordion_btn)
            time.sleep(1)
        except:
            self.driver.get(self.url)
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, HEADING_BUTTON)))
        time.sleep(1)
        
    def wait_for_results_refresh(self):
        try:
            old_table = self.driver.find_element(By.CSS_SELECTOR, "#results table")
            WebDriverWait(self.driver, 10).until(EC.staleness_of(old_table))
            # now wait for new table to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#results table tbody tr"))
            )
            print("🔄 Results refreshed.")
        except Exception as e:
            print("⚠️ Results did not refresh properly:", e)

    def close(self):
        self.driver.quit()
