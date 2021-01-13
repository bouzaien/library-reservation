from datetime import datetime, timedelta
import logging
import os
import pickle
import requests
import time

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import schedule

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
load_dotenv(verbose=True)

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
LOGIN_URL = "https://hbzwwws005.uzh.ch/booked-ubzh-extern/Web/index.php"
UPDATE_URL = "https://hbzwwws005.uzh.ch/booked-ubzh-extern/Web/ajax/reservation_update.php"

payload = {
	"email": EMAIL,
	"password": PASSWORD,
	"captcha": "",
	"login": "submit",
	"resume": "",
	"language": "en_us"
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

def update():
    logging.info("Running update ...")

    update_data = {
        "userId" : "312",
        "scheduleId" : "21",
        "reservationAction" : "update",
        "seriesUpdateScope" : "full"
    }


    update_data["beginDate"] = (datetime.today() + timedelta(7)).strftime('%Y-%m-%d')
    update_data["endDate"] = (datetime.today() + timedelta(7)).strftime('%Y-%m-%d')
    update_data["beginPeriod"] = "08:00:00"
    update_data["endPeriod"] = datetime.now().replace(minute=0, second=0).strftime("%H:%M:%S")

    with open('refs.pkl','rb') as f:
        refs = pickle.load(f)
    reference_number = refs[update_data["beginDate"]][0]
    resource_id = refs[update_data["beginDate"]][1]
    update_data["referenceNumber"] = reference_number
    update_data["resourceId"] = resource_id

    logging.info("Updating reservation {} ...".format(reference_number))

    with requests.Session() as s:
        logging.info("Session started.")
        p = s.post(LOGIN_URL, data=payload)
        logging.info("Logged in as {}.".format(payload["email"]))
        soup = BeautifulSoup(p.text, features="html.parser")
        csrf_token = soup.select_one('input[id="csrf_token"]')['value']
        update_data["CSRF_TOKEN"] = csrf_token
        logging.info("CSRF_TOKEN: {}".format(csrf_token))

        s.headers.update(headers_dict)

        r = s.post(UPDATE_URL, data=update_data)
        try:
            soup = BeautifulSoup(r.text, features="html.parser")
            update_message = soup.select_one('div[id="created-message"]').getText()
            logging.info(update_message)
        except:
            logging.info("Update failed.")

if __name__ == "__main__":
    logging.info("Script running ...")
    for hour in list(str(h)+':00:00' for h in range(9,17+1)):
        schedule.every().day.at(hour).do(update)

    while True:
        schedule.run_pending()
        time.sleep(1)
