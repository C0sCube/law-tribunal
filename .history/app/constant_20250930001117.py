from datetime import datetime
import json, json5, os


def create_dirs(root_path: str, dirs: list) -> list:
    created_paths = []
    for dir_name in dirs:
        full_path = os.path.join(root_path, dir_name)
        os.makedirs(full_path, exist_ok=True)
        created_paths.append(full_path)
    return created_paths if len(created_paths) > 1 else created_paths[0]


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_json5(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


CONFIG = {
    "url": "https://itat.gov.in/judicial/tribunalorders",
    "benches": [20],        # can be list [20,21,22] or range via start..end
    "appeals": [1, 2, 3],   # same as above
    "dates": ["28/09/2025"], # allow multiple or a range
    "max_attempts": 5,
    "output_dir": "results",
    "browser": {
        "headless": False,
        "suppress_logs": True
    }
}



#WEBSITE URL DATA
DEFAULT_TODAY_DATE = datetime.today().strftime("%d/%m/%Y")
WEBSITE_URL = r"https://itat.gov.in/judicial/tribunalorders"

DEFAULT_WAIT_TIME = 10

# SELENIUM WINDOW CONSTANTS
WINDOW_WIDTH = 700
WINDOW_HEIGHT =900
DEFAULT_WAIT = 2


CAPTCHA_MP3_PATH = r"app\temp\captcha.mp3"
CAPTCHA_WAV_PATH = r"app\temp\captcha.wav"
FFMPEG_PATH = r"C:\Users\kaustubh.keny\ffmpeg-8.0-essentials_build\bin"


BENCH_DROPDOWN = "//select[@id='ddlBench']"
APPEAL_DROPDOWN = "//select[@id='ddlAppeal']"

HEADING_BUTTON = "#headingTwo button"
BENCH_SELECT = "bench_name_2"
APPLIC_SELECT = "app_type_2"
DATE_SELECT = "order_date"

AUDIO_PLAY_BUTTON = "//img[@alt='Play Icon']"
AUDIO_SOURCE = "captchaAudio"

CAPTCHA_REFRESH =  "//img[@alt='Refresh Icon']"

SUBMIT_CAPTCHA_BUTTON = "b2"
CAPTCHA_ID =  "captcha"

PAGE_BTN_XPATH = "//input[@name='btnPage']"