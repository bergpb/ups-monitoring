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
                cur = con.cursor()
                cur.execute(
                    """
                        CREATE TABLE IF NOT EXISTS battery (
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
                cur = con.cursor()
                datetime = strftime("%Y-%m-%d %H:%M:%S")

                res = cur.execute(
                    """
                        SELECT voltage, capacity, status
                            FROM battery
                            ORDER BY ID DESC
                            LIMIT 1;
                    """
                ).fetchone()

                if res is not None:
                    previous_voltage = res[0]
                    previous_capacity = res[1]
                    previous_status = res[2]

                    if (previous_voltage == voltage and
                        previous_capacity == capacity and
                        previous_status == status):
                        logger.info('Previous values are the same, skipping...')
                        return

                # https://stackoverflow.com/a/32339569/6539270
                con.execute(
                    """
                        INSERT INTO battery VALUES (NULL, ?, ?, ?, ?);
                    """,
                    (voltage, capacity, status, datetime),
                )
                self.con.commit()

        except Exception as error:
            logger.error(f"Error: {type(error)}: {error}")


    def drop_table(self):
        try:
            with self.con as con:
                cur = con.cursor()
                cur.execute("""DROP TABLE battery;""")
                self.con.commit()

        except Exception as error:
            logger.error(f"Error: {type(error)}: {error}")
