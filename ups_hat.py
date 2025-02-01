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

logger = logging.getLogger(__name__)

DRY_RUN = getenv("DRY_RUN", False)

if not DRY_RUN:
    from ext.ups import UPS
    import RPi.GPIO as GPIO

    ups = UPS()

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(4, GPIO.IN)

logger.debug('Setting send value to 1 - initial value')
datetime = strftime("%Y-%m-%d %H:%M:%S")
db.execute('UPDATE notification SET send = ?, datetime = ? WHERE id = 1;', 1, datetime)


def shutdown():
    if not DRY_RUN:
        command = "/usr/bin/sudo /sbin/shutdown -h +1"
        subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        logger.critical('Very low battery!!!')


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
            logger.info('Sending notification to Gotify!')
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    logger.debug('Setting send value to 0 - notification sent')
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
        logger.debug(f"Running in dry run mode!!!")

    if not DRY_RUN:
        if GPIO.input(4) == GPIO.HIGH:
            status = 1
            battery_status = "charging"
            logger.debug("Power Adapter Plugged In")
            logger.debug('Setting send value to 1 - charger plugged')
            db.execute('UPDATE notification SET send = ?, datetime = ? WHERE id = 1;', 1, datetime)
        if GPIO.input(4) == GPIO.LOW:
            logger.debug("Power Adapter Unplugged")
            logger.debug('Setting send value to 1 - charger unplugged')

    logger.info(f"Status: {battery_status}, Battery: {capacity:.0f}%, Voltage: {current_voltage:.2f}V")

    db.insert(current_voltage, capacity, status)

    if not status:
        if capacity <= 20 and capacity > 10:
            send = db.execute('SELECT send FROM notification WHERE id = 1;')[0]
            if send:
                msg = f"Low battery ({capacity:.0f}%), please plug the charger!!!"
                logger.info(msg)
                send_notification(msg, send)
        elif capacity <= 10:
            logger.critical("BATTERY RUNNING OUT!!!")
            logger.info("Shutting down...")
            shutdown()

    logger.info('----------------------------------------------------------------------------')


if __name__ == "__main__":
    schedule.every(1).minutes.do(job)

    while True:
        schedule.run_pending()
        sleep(1)
