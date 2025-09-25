from datetime import datetime

#WEBSITE URL DATA
DEFAULT_TODAY_DATE = datetime.today().strftime("%d/%m/%Y")
WEBSITE_URL = r"https://itat.gov.in/judicial/tribunalorders"


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

SUBMIT_CAPTCHA_BUTTON = "b2"
CAPTCHA_ID =  "captcha"

PAGE_BTN_XPATH = "//input[@name='btnPage']"