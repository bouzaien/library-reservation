from datetime import datetime, timedelta
import json
import logging
import os
import pickle
import requests
import sys
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
RESERVATION_URL = "https://hbzwwws005.uzh.ch/booked-ubzh-extern/Web/ajax/reservation_save.php"
UPDATE_URL = "https://hbzwwws005.uzh.ch/booked-ubzh-extern/Web/ajax/reservation_update.php"
RIDs = list(range(1239,1252+1))

# Variables
payload = {
	"email": EMAIL,
	"password": PASSWORD,
	"captcha": "",
	"login": "submit",
	"resume": "",
	"language": "en_us"
}

data = {
    "userId" : "312",
    "beginPeriod" : "08:00:00",
    "endPeriod" : "09:00:00",
    "scheduleId" : "21",
    "resourceId" : "1243",
    "reservationDescription" : "Revision",
    "TOS_ACKNOWLEDGEMENT" : "on",
    "reservationAction" : "create",
    "seriesUpdateScope" : "full"
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

def reservation():
    logging.info("Started reservation.")
    reservation_date = (datetime.today() + timedelta(7)).strftime('%Y-%m-%d')
    reservation_begin_hour = "08:00:00"
    reservation_end_hour = "09:00:00"

    data["beginDate"] = reservation_date
    data["endDate"] = reservation_date
    data["beginPeriod"] = reservation_begin_hour
    data["endPeriod"] = reservation_end_hour

    table_num = int(data["resourceId"]) - 909

    if datetime.today().strftime("%A") in ['Saturday', 'Sunday']:
        data["scheduleId"] = "20"
        data["resourceId"] = "1233"
        table_num = int(data["resourceId"]) - 723

    logging.info("From {} {} to {} {} @{}.".format(reservation_begin_hour,reservation_date,reservation_end_hour,reservation_date, table_num))

    with requests.Session() as s:
        logging.info("Session started.")
        p = s.post(LOGIN_URL, data=payload)
        logging.info("Logged in as {}.".format(payload["email"]))
        soup = BeautifulSoup(p.text, features="html.parser")
        csrf_token = soup.select_one('input[id="csrf_token"]')['value']
        data["CSRF_TOKEN"] = csrf_token
        logging.info("CSRF_TOKEN: {}".format(csrf_token))

        s.headers.update(headers_dict)

        r = s.post(RESERVATION_URL, data=data)
        soup = BeautifulSoup(r.text, features="html.parser")
        try:
            reservation_message = soup.select_one('div[id="created-message"]').getText()
            reference_message = soup.select_one('div[id="reference-number"]').getText()
            reference_number = reference_message.split()[-1]
            logging.info(reservation_message)
            logging.info(reference_message)
            with open('refs.pkl', 'rb') as f:
                refs = pickle.load(f)
            refs[reservation_date] = [reference_number, data["resourceId"]]
            with open('refs.pkl', 'wb') as f:
                pickle.dump(refs, f)
        except:
            logging.info("Reservation failed.")


if __name__ == "__main__":
    logging.info("Script running ...")
    schedule.every().day.at("09:00:00").do(reservation)
    while True:
        schedule.run_pending()
        time.sleep(1)
