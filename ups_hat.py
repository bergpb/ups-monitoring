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

DRY_RUN = getenv("DRY_RUN", True)

if not DRY_RUN:
    import RPi.GPIO as GPIO

    from ext.ups import UPS

    ups = UPS()


def shutdown():
    command = "/usr/bin/sudo /sbin/shutdown -h +1"
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    send_notification(output)


def send_notification(msg):
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
    if not DRY_RUN:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(4, GPIO.IN)

        current_voltage = ups.read_voltage()
        capacity = ups.read_capacity()

        # retry if ready isn't working
        while capacity == 0 or current_voltage == 0:
            current_voltage = ups.read_voltage()
            capacity = ups.read_capacity()
    else:
        logger.info(f"Running in dry run mode!!!")

        current_voltage = 3.9
        capacity = 90

    logger.info(f"Battery: {capacity:.0f}%, {current_voltage:.2f}V")

    status = 1
    if not DRY_RUN:
        if GPIO.input(4) == GPIO.HIGH:
            status = 1
            logger.info("Power Adapter Plug In")
        if GPIO.input(4) == GPIO.LOW:
            logger.info("Power Adapter Unplug")

    db.insert(current_voltage, capacity, status)

    if capacity <= 25 and capacity > 10:
        msg = f"Low battery ({capacity:.0f}%), please plug the charger!!!"
        send_notification(msg)
    elif capacity <= 10:
        logger.critical("D A N G E R !!!")
        logger.critical("BATTERY RUNNING OUT")
        msg = "Danger: The device will turn off soon due energy power!"
        send_notification(msg)
        logger.critical("Shutting down........")
        shutdown()


if not DRY_RUN:
    schedule.every(1).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
else:
    job()
