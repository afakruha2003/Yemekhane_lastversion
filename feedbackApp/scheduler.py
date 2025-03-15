import schedule
import threading
import time
from datetime import datetime
from feedbackApp.gemini import do_everything


schedule.every().day.at("01:00").do(do_everything)

def schedule_runner():
    while True:
        schedule.run_pending()
        time.sleep(600)  # Her 10 dakikada bir kontrol et
