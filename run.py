from datetime import datetime, timedelta
import json
import os
import requests
import sys
import time

from bs4 import BeautifulSoup
from dotenv import load_dotenv
import schedule

load_dotenv(verbose=True)

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

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
    "beginDate" : "2021-01-15",
    "beginPeriod" : "08:00:00",
    "endDate" : "2021-01-15",
    "endPeriod" : "09:00:00",
    "scheduleId" : "21",
    "resourceId" : "1252",
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

LOGIN_URL = "https://hbzwwws005.uzh.ch/booked-ubzh-extern/Web/index.php"
RESERVATION_URL = "https://hbzwwws005.uzh.ch/booked-ubzh-extern/Web/ajax/reservation_save.php"

RIDs = list(range(1239,1252+1))

def reservation():
    reservation_date = (datetime.today() + timedelta(7)).strftime('%Y-%m-%d')
    reservation_begin_hour = datetime.now().replace(minute=0, second=0).strftime("%H:%M:%S")
    reservation_end_hour = (datetime.now().replace(minute=0, second=0) + timedelta(hours=1)).strftime("%H:%M:%S")

    data["beginDate"] = reservation_date
    data["endDate"] = reservation_date
    data["beginPeriod"] = reservation_begin_hour
    data["endPeriod"] = reservation_end_hour

    with requests.Session() as s:

        p = s.post(LOGIN_URL, data=payload)

        soup = BeautifulSoup(p.text, features="html.parser")
        csrf_token = soup.select_one('input[id="csrf_token"]')['value']
        data["CSRF_TOKEN"] = csrf_token

        s.headers.update(headers_dict)

        r = s.post(RESERVATION_URL, data=data)
        print(r)

schedule.every().day.at("08:00").do(reservation)
schedule.every().day.at("09:00").do(reservation)
schedule.every().day.at("10:00").do(reservation)
schedule.every().day.at("01:56:40").do(reservation)

while True:
    schedule.run_pending()
    time.sleep(1)