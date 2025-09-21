import requests
from tkinter import Tk
from app.ui import AppUI
from app.scraper import TribunalScraper
from app.captcha_solver import download_audio, recognize_audio
from app.constant import *

def run_all(ui):
    # read bench & date from UI
    bench_code = ui.bench_var.get().split(" - ")[0]  # e.g. "199" from "199 - Mumbai"
    date = ui.date_var.get().strip() or DEFAULT_TODAY_DATE

    scraper = TribunalScraper(WEBSITE_URL)
    scraper.start()

    for appeal_index in range(1, 19): # all appeals
        if not ui.running:
            scraper.close()
            ui.log("Stopped by user.")
            return

        # === NEW: Wait for Next Combo button ===
        if appeal_index == 1:  # only wait once per bench, before appeals loop
            ui.wait_for_next()

        # Set selections
        bench_name, appeal_name = scraper.set_search_options(bench_code, appeal_index, date)
        ui.log(f"Processing Bench: {bench_name}, Appeal: {appeal_name}, Date: {date}")


        # CAPTCHA
        audio_src = scraper.get_captcha_audio()
        session = requests.Session()
        for cookie in scraper.driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        wav_path = download_audio(session, audio_src)
        captcha_guess = recognize_audio(wav_path)

        ui.show_captcha_guess(captcha_guess)
        ui.captcha_event.clear()
        ui.log("Waiting for CAPTCHA confirmation...")
        ui.captcha_event.wait()
        captcha_value = ui.captcha_value

        scraper.submit_captcha(captcha_value)
        scraper.wait_for_results_refresh()

        # Results
        data = scraper.scrape_results(bench_name, appeal_name, ui)
        if data is not None and not data.empty:
            filename = f"{bench_name}_{appeal_name}.xlsx".lower().replace(" ", "_")
            data.to_excel(filename, index=False)
            ui.log(f"✅ Saved results: {filename}")
        else:
            ui.log("⚠️ No data found.")

        scraper.reset_form()

    scraper.close()
    ui.log("🎉 Finished all appeals for selected bench.")

if __name__ == "__main__":
    root = Tk()
    app = AppUI(root, run_all)
    root.mainloop()
