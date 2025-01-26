import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

path = Path.cwd()

default_formatter = logging.Formatter(
    "%(asctime)s %(name)s [%(levelname)s] %(message)s"
)

handler = RotatingFileHandler(
    filename=f"{path}/ups.log", maxBytes=1000000, backupCount=5
)

handler.setLevel(logging.INFO)
handler.setFormatter(default_formatter)

ups = logging.getLogger()
ups.addHandler(handler)
ups.setLevel(logging.INFO)
