import logging
import subprocess
import time
from datetime import datetime as dt
from os import getenv

import requests
import schedule
from dotenv import load_dotenv

from ext import log
from ext.db import Database

load_dotenv()

db = Database("ups")

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


def send_notification(msg):
    if not DRY_RUN:
        server = getenv("GOTIFY_SERVER")
        token = getenv("GOTIFY_TOKEN")

        try:
            requests.post(
                f"{server}/message?token={token}",
                json={"message": msg, "priority": 0, "title": "UPS Battery Low"},
            )
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")


def job():
    status = 0
    battery_status = "discharging"
    if not DRY_RUN:
        current_voltage = ups.read_voltage()
        capacity = ups.read_capacity()

        # retry if ready isn't working
        while capacity == 0 or current_voltage == 0:
            current_voltage = ups.read_voltage()
            capacity = ups.read_capacity()
    else:
        capacity = 10
        current_voltage = 4
        logger.info(f"Running in dry run mode!!!")

    if not DRY_RUN:
        if GPIO.input(4) == GPIO.HIGH:
            status = 1
            battery_status = "charging"
            logger.info("Power Adapter Plugged In")
        if GPIO.input(4) == GPIO.LOW:
            logger.info("Power Adapter Unplugged")

    logger.info(f"Status: {battery_status}, Battery: {capacity:.0f}%, Voltage: {current_voltage:.2f}V")

    db.insert(current_voltage, capacity, status)

    if capacity <= 25 and capacity > 10:
        msg = f"Low battery ({capacity:.0f}%), please plug the charger!!!"
        send_notification(msg)
    elif not status and capacity <= 10:
        logger.critical("D A N G E R !!!")
        logger.critical("BATTERY RUNNING OUT")
        msg = "Danger: The device will turn off soon due energy power!"
        send_notification(msg)
        logger.info("Shutting down...")
        shutdown()


if not DRY_RUN:
    schedule.every(2).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
else:
    job()
