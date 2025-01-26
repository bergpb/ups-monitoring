import sqlite3
from time import strftime

from ext.log import logging

logger = logging.getLogger("ups.db")


class Database:
    def __init__(self, db):
        self.db = db
        self.con = sqlite3.connect(db + ".sqlite3")


    def create_table(self):
        try:
            with self.con as con:
                con.execute(
                    """
                        CREATE TABLE IF NOT EXISTS battery_status (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            voltage REAL NOT NULL,
                            capacity INTEGER NOT NULL,
                            status INTEGER NOT NULL,
                            datetime TIMESTAMP NOT NULL
                        );
                    """
                )
                self.con.commit()

        except Exception as error:
            logger.error(f"Error: {type(error)}: {error}")


    def insert(self, voltage, capacity, status):
        self.create_table()
        try:
            with self.con as con:
                datetime = strftime("%Y-%m-%d %H:%M:%S")
                con.execute(
                    """
                        INSERT INTO battery_status (voltage, capacity, status, datetime) VALUES (?, ?, ?, ?);
                    """,
                    (voltage, capacity, status, datetime),
                )
                self.con.commit()

        except Exception as error:
            logger.error(f"Error: {type(error)}: {error}")


    def drop_table(self):
        try:
            with self.con as con:
                con.execute("""DROP TABLE battery_status;""")
                self.con.commit()

        except Exception as error:
            logger.error(f"Error: {type(error)}: {error}")
