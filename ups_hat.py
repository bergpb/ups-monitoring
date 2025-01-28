import logging
import subprocess
from time import sleep, strftime
from datetime import datetime as dt
from os import getenv

import requests
import schedule
from dotenv import load_dotenv

from ext import log
from ext.db import Database

load_dotenv()

db = Database("ups")
db.create_tables()

logger = logging.getLogger("ups.main")

DRY_RUN = getenv("DRY_RUN", False)

if not DRY_RUN:
    from ext.ups import UPS
    import RPi.GPIO as GPIO

    ups = UPS()

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(4, GPIO.IN)


def shutdown():
    if not DRY_RUN:
        command = "/usr/bin/sudo /sbin/shutdown -h +1"
        subprocess.Popen(command.split(), stdout=subprocess.PIPE)


def send_notification(msg, send):
    datetime = strftime("%Y-%m-%d %H:%M:%S")
    if not DRY_RUN and send:
        server = getenv("GOTIFY_SERVER")
        token = getenv("GOTIFY_TOKEN")
        try:
            requests.post(
                f"{server}/message?token={token}",
                json={"message": msg, "priority": 0, "title": "UPS Battery Low"},
            )
            logger.info('Sending notification to Gotify')
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    elif send:
        logger.debug('Logging fake notification!')
    db.execute('UPDATE notification SET send = ?, datetime = ? WHERE id = 1;', 0, datetime)


def job():
    status = 0
    battery_status = "discharging"
    datetime = strftime("%Y-%m-%d %H:%M:%S")
    if not DRY_RUN:
        current_voltage = ups.read_voltage()
        capacity = ups.read_capacity()

        while capacity == 0 or current_voltage == 0:
            current_voltage = ups.read_voltage()
            capacity = ups.read_capacity()
    else:
        capacity = 15
        current_voltage = 4
        logger.info(f"Running in dry run mode!!!")

    if not DRY_RUN:
        if GPIO.input(4) == GPIO.HIGH:
            status = 1
            battery_status = "charging"
            logger.debug("Power Adapter Plugged In")
        if GPIO.input(4) == GPIO.LOW:
            logger.debug("Power Adapter Unplugged")
            db.execute('UPDATE notification SET send = ?, datetime = ? WHERE id = 1;', 1, datetime)

    logger.info(f"Status: {battery_status}, Battery: {capacity:.0f}%, Voltage: {current_voltage:.2f}V")

    db.insert(current_voltage, capacity, status)

    if not status and (capacity <= 25 and capacity > 5):
        msg = f"Low battery ({capacity:.0f}%), please plug the charger!!!"
        send = db.execute('SELECT send FROM notification ORDER BY id DESC LIMIT 1;')[0]
        logger.info(msg)
        send_notification(msg, send)
    elif not status and capacity <= 5:
        logger.critical("BATTERY RUNNING OUT!!!")
        logger.info("Shutting down...")
        shutdown()
    else:
        db.execute('UPDATE notification SET send = ?, datetime = ? WHERE id = 1;', 0, datetime)

    logger.info('----------------------------------------------------------------------------')

if not DRY_RUN:
    schedule.every(2).minutes.do(job)

    while True:
        schedule.run_pending()
        sleep(1)
else:
    job()
