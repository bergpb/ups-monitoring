import logging
from os import getenv
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

path = Path.cwd()

log_level = getenv("LOG_LEVEL", "INFO").upper()

default_formatter = logging.Formatter(
    "%(asctime)s %(name)s [%(levelname)s] %(message)s"
)

handler = RotatingFileHandler(
    filename=f"{path}/ups.log", maxBytes=1000000, backupCount=5
)

handler.setLevel(log_level)
handler.setFormatter(default_formatter)

ups = logging.getLogger()
ups.addHandler(handler)
ups.setLevel(log_level)
