import os, requests
from pydub import AudioSegment
from pydub.effects import normalize
import speech_recognition as sr

from app.constant import CAPTCHA_MP3_PATH, CAPTCHA_WAV_PATH, FFMPEG_PATH

def download_audio(session, url):
    response = session.get(url)
    with open(CAPTCHA_MP3_PATH, "wb") as f:
        f.write(response.content)

    os.environ["PATH"] += os.pathsep + FFMPEG_PATH
    sound = AudioSegment.from_file(CAPTCHA_MP3_PATH, format="mp3")
    sound = sound.set_channels(1).set_frame_rate(16000)
    sound = normalize(sound)
    sound = sound.strip_silence(silence_len=300, silence_thresh=-40)
    sound.export(CAPTCHA_WAV_PATH, format="wav")
    return CAPTCHA_WAV_PATH

def recognize_audio(wav_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio_data).upper().replace(" ", "")
    except:
        return ""
