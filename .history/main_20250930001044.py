import time,logging  #type:ignore
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By                # Locators (ID, CLASS_NAME, XPATH, etc.)
from selenium.webdriver.support.ui import WebDriverWait       # Waits for elements to appear
from selenium.webdriver.support import expected_conditions as EC  # Conditions like "visible", "clickable"
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

from app.constant import *
from app.logger import setup_logger, set_global_logger
from app.web_scraper import TribunalWebScraper
from app.captcha_solver import recognize_audio


logger = setup_logger("law_scraper",log_dir="logs", log_level=logging.DEBUG)
set_global_logger(logger)

def runner(driver, bench_index, appeal_index, dateTake, cfg):
    MAX_ATTEMPTS = cfg.get("max_attempts", 5)
    success = False
    attempt = 0
    
    scraper = TribunalWebScraper(driver)
    logger.info(f"Running for {bench_index}; {appeal_index}.")
    
    while attempt < MAX_ATTEMPTS and not success:
        if attempt == 0:
            driver.get(cfg["url"])
        logger.info(f"Attempt: {attempt + 1}")
        attempt += 1
        try:
            accordion_btn = scraper.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, HEADING_BUTTON))
            )
            driver.execute_script("arguments[0].click();", accordion_btn)

            bench_name, appeal_name, date_used = scraper.set_search_options(
                bench_index, appeal_index, dateTake
            )

            audio_url = scraper.get_captcha_audio()
            data = recognize_audio(scraper.driver, audio_url)
            scraper.submit_captcha(data)

            try:
                WebDriverWait(driver, 5).until(EC.alert_is_present())
                alert = scraper.driver.switch_to.alert
                logger.warning(f"Alert says: {alert.text}")
                alert.accept()
                logger.info("Refreshing website to get new captcha...")
                scraper.driver.refresh()
                continue
            except TimeoutException:
                logger.info("No alert — CAPTCHA accepted!")
                success = True
                time.sleep(0.5)
                break
        except Exception as e:
            logger.error(f"Failed during attempt {attempt}: {e}")
            time.sleep(0.5)

    if success and scraper.check_results_loaded():
        df = scraper.scrape_results(bench_name, appeal_name)
        if isinstance(df, pd.DataFrame) and not df.empty:
            out_path = f"{cfg['output_dir']}/{bench_name}_{appeal_name}.xlsx"
            df.to_excel(out_path, index=False)
            logger.info(f"Data saved at {out_path}.")
        else:
            logger.info("No valid data to save or scraping failed.")
    else:
        logger.warning("No results found or CAPTCHA failed after max attempts.")
