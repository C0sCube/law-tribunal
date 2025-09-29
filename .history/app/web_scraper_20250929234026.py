import time
import pandas as pd
# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException

from app.constant import *
from app.logger import get_global_logger

logger = get_global_logger()

class TribunalWebScraper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_WAIT_TIME)
        self.logger = logger

    def set_search_options(self, bench_index: int, appeal_index: int, date: str):
        try:
            bench_name = self._select_dropdown_option(BENCH_SELECT, bench_index, "Bench")
            appeal_name = self._select_dropdown_option(APPLIC_SELECT, appeal_index, "Appeal")
            self._set_date(date)
            self.logger.info(f"Search options set: Bench='{bench_name}', Appeal='{appeal_name}', Date='{date}'")
            return bench_name, appeal_name, date
        except Exception as e:
            self.logger.error(f"Failed to set search options: {e}")
            raise

    def _select_dropdown_option(self, element_id, index, label):
        dropdown = self.wait.until(EC.visibility_of_element_located((By.ID, element_id)))
        select = Select(dropdown)
        if index >= len(select.options):
            raise ValueError(f"{label} index {index} out of range.")
        select.select_by_index(index)
        return select.first_selected_option.text

    def _set_date(self, date):
        date_input = self.wait.until(EC.visibility_of_element_located((By.ID, DATE_SELECT)))
        self.driver.execute_script("arguments[0].removeAttribute('readonly')", date_input)
        self.driver.execute_script("arguments[0].value = arguments[1];", date_input, date)
        self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", date_input)

    def get_captcha_audio(self):
        audio_btn = self.driver.find_element(By.XPATH, AUDIO_PLAY_BUTTON)
        self._click_element(audio_btn)
        time.sleep(.5)
        return self.driver.find_element(By.ID, AUDIO_SOURCE).get_attribute("src")

    def refresh_captcha(self):
        refresh_btn = self.driver.find_element(By.XPATH, AUDIO_PLAY_BUTTON)
        self._click_element(refresh_btn)
        time.sleep(.5)

    def submit_captcha(self, captcha_text: str):
        captcha_input = self.driver.find_element(By.ID, CAPTCHA_ID)
        captcha_input.clear()
        self.logger.info(f"Sending Text: {captcha_text}")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", captcha_input)
        captcha_input.send_keys(captcha_text)
        submit_btn = self.driver.find_element(By.ID, SUBMIT_CAPTCHA_BUTTON)
        time.sleep(.5)
        self._click_element(submit_btn)

    def _click_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        self.driver.execute_script("arguments[0].click();", element)

    def check_results_loaded(self):
        try:
            rows = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#results table tbody tr")))
            if rows:
                self.logger.info(f"Results loaded with {len(rows)} row(s).")
                return True
            self.logger.warning("Results table found but no rows present.")
            return False
        except Exception as e:
            self.logger.error(f"Error checking results: {e}")
            return False

    def scrape_results(self, bench_name, appeal_name):
        self.logger.info("Page Loaded.")
        try:
            self.wait.until(lambda d: (
                d.find_elements(By.CSS_SELECTOR, "#results table tbody tr td[colspan='5']")
                or d.find_elements(By.CSS_SELECTOR, "#results table tbody tr td:nth-child(2)")
            ))
        except Exception:
            self.logger.warning("Results table did not load.")
            return None

        no_data_cells = self.driver.find_elements(By.CSS_SELECTOR, "#results table tbody tr td[colspan='5']")
        if no_data_cells and "No Records Found" in no_data_cells[0].text:
            self.logger.warning("No records found. Skipping pagination.")
            return None

        page_buttons = self.driver.find_elements(By.XPATH, PAGE_BTN_XPATH)
        max_pages = len(page_buttons) if page_buttons else 1
        self.logger.info(f"Total Pages are {max_pages}.")

        data, seen_links = [], set()

        for page_num in range(1, max_pages + 1):
            try:
                page_btn = self.driver.find_element(By.XPATH, f"//input[@name='btnPage' and @value='{page_num}']")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", page_btn)

                if page_btn.get_attribute("disabled"):
                    self.logger.info(f"Skipping page {page_num} (already active).")
                else:
                    self.driver.execute_script("arguments[0].click();", page_btn)
                    self.logger.info(f"-> Clicked page {page_num}")
                    self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#results table tbody tr")))
                    time.sleep(1.5)

                rows = self.driver.find_elements(By.CSS_SELECTOR, "#results table tbody tr")
                page_new_count = 0

                for row in rows:
                    try:
                        parties = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)").text.strip()
                        order_link = row.find_element(By.CSS_SELECTOR, "td:nth-child(4) a").get_attribute("href")
                        if order_link and order_link not in seen_links:
                            seen_links.add(order_link)
                            data.append([bench_name, appeal_name, parties, order_link])
                            page_new_count += 1
                    except Exception:
                        continue

                self.logger.info(f"Rows on page {page_num}: {len(rows)} | new added: {page_new_count}")
            except Exception as e:
                self.logger.warning(f"Failed to process page {page_num}: {e}")
                continue

        if data:
            df = pd.DataFrame(data, columns=["Bench", "Appeal", "Parties", "Order Link"])
            df["Order Link"] = df["Order Link"].apply(lambda url: f'=HYPERLINK("{url}", "{url}")')
            logger.info(f"Scraped Data Preview:\n{df.head(5)}")
            return df
        return None