from datetime import datetime, timedelta
import logging
import os
import pickle
import requests
import time

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import schedule

# Configs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
load_dotenv(verbose=True)

# Constants
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
LOGIN_URL = "https://hbzwwws005.uzh.ch/booked-ubzh-extern/Web/index.php"
CHECKIN_URL = "https://hbzwwws005.uzh.ch/booked-ubzh-extern/Web/ajax/reservation_checkin.php?action=checkin"

# Variables
payload = {
	"email": EMAIL,
	"password": PASSWORD,
	"captcha": "",
	"login": "submit",
	"resume": "",
	"language": "en_us"
}

checkin_data = {
	"userId": "312",
	"beginPeriod": "08:00:00",
	"endPeriod": "18:00:00",
	"scheduleId": "21",
	"resourceId": "1243",
	"reservationDescription": "",
	"START_REMINDER_ENABLED": "off",
	"START_REMINDER_TIME": "15",
	"START_REMINDER_INTERVAL": "minutes",
	"reservationAction": "update",
	"seriesUpdateScope": "full"
}

headers_dict = {
    "Host": "hbzwwws005.uzh.ch",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://hbzwwws005.uzh.ch",
    "Connection": "keep-alive",
    "Referer": "https://hbzwwws005.uzh.ch/booked-ubzh-extern/Web/reservation.php",
}

def checkin():
    logging.info("Running checkin ...")

    checkin_data["beginDate"] = datetime.today().strftime('%Y-%m-%d')
    checkin_data["endDate"] = datetime.today().strftime('%Y-%m-%d')

    with open('refs.pkl','rb') as f:
        refs = pickle.load(f)
    reference_number = refs[checkin_data["beginDate"]][0]
    resource_id = refs[checkin_data["beginDate"]][1]
    checkin_data["referenceNumber"] = reference_number
    checkin_data["resourceId"] = resource_id

    logging.info("Performing checking for reservation {} ...".format(reference_number))

    with requests.Session() as s:
        logging.info("Session started.")
        p = s.post(LOGIN_URL, data=payload)
        logging.info("Logged in as {}.".format(payload["email"]))
        soup = BeautifulSoup(p.text, features="html.parser")
        csrf_token = soup.select_one('input[id="csrf_token"]')['value']
        checkin_data["CSRF_TOKEN"] = csrf_token
        logging.info("CSRF_TOKEN: {}".format(csrf_token))

        s.headers.update(headers_dict)

        r = s.post(CHECKIN_URL, data=checkin_data)
        try:
            soup = BeautifulSoup(r.text, features="html.parser")
            update_message = soup.select_one('div[id="checked-in-message"]').getText()
            logging.info(update_message)
        except:
            logging.info("Checkin failed.")

if __name__ == "__main__":
    logging.info("Script running ...")
    schedule.every().day.at("08:00:00").do(checkin)

    while True:
        schedule.run_pending()
        time.sleep(1)