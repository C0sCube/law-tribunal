import os, requests, re, ffmpeg
# from pydub import AudioSegment
# from pydub.effects import normalize
# import speech_recognition as sr
import whisper #type:ignore

from app.logger import get_global_logger
from app.constant import CAPTCHA_MP3_PATH, FFMPEG_PATH, CAPTCHA_WAV_PATH

logger = get_global_logger()

# def preprocess_audio(input_path, output_path):
#     (
#         ffmpeg
#         .input(input_path)
#         .output(output_path, ac=1, ar=16000, format="wav", loglevel="quiet")
#         .overwrite_output()
#         .run()
#     )

def recognize_audio(driver, url):
    session = requests.Session()
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])

    os.environ["PATH"] += os.pathsep + FFMPEG_PATH
    response = session.get(url)
    with open(CAPTCHA_MP3_PATH, "wb") as f:
        f.write(response.content)

    # preprocess
    # preprocess_audio(CAPTCHA_MP3_PATH, CAPTCHA_WAV_PATH)

    logger.info("Beginning to detect audio...")
    model = whisper.load_model("small.en")  # improved model
    result = model.transcribe(CAPTCHA_MP3_PATH,language="en",initial_prompt="The audio contains only letters and numbers.")

    data = result["text"]
    correct_data = "".join(c for c in data if c.isalnum()).upper()
    logger.info(f"Language: {result['language']}  |  Transcription: {correct_data}")
    return correct_data


# def recognize_audio(driver,url):
    
#     #create session
#     session = requests.Session()
#     for cookie in driver.get_cookies():
#         session.cookies.set(cookie['name'], cookie['value'])
    
#     response = session.get(url)
#     with open(CAPTCHA_MP3_PATH, "wb") as f:
#         f.write(response.content)
#     logger.info(f"Beginning to detect audio...")
#     model = whisper.load_model("base")
#     result = model.transcribe(CAPTCHA_MP3_PATH) #detect value
#     data = result["text"]
    
#     matches = re.findall(r"[A-Za-z0-9]+",data,re.IGNORECASE)
#     correct_data = "".join(matches).upper()
#     logger.info(f"Detected language:{result["language"]}\tTranscription:{correct_data}")
#     return correct_data

        
# def download_audio(session, url):
#     response = session.get(url)
#     with open(CAPTCHA_MP3_PATH, "wb") as f:
#         f.write(response.content)

#     os.environ["PATH"] += os.pathsep + FFMPEG_PATH
#     sound = AudioSegment.from_file(CAPTCHA_MP3_PATH, format="mp3")
#     sound = sound.set_channels(1).set_frame_rate(16000)
#     sound = normalize(sound)
#     sound = sound.strip_silence(silence_len=300, silence_thresh=-40)
#     sound.export(CAPTCHA_WAV_PATH, format="wav")
#     return CAPTCHA_WAV_PATH

# def recognize_audio(wav_path):
#     recognizer = sr.Recognizer()
#     with sr.AudioFile(wav_path) as source:
#         audio_data = recognizer.record(source)
#     try:
#         return recognizer.recognize_google(audio_data).upper().replace(" ", "")
#     except:
#         return ""
