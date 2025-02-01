import sqlite3
from time import strftime

from ext.log import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db):
        self.db = db
        self.con = sqlite3.connect(db + ".sqlite3")


    def create_tables(self):
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

                cur.execute(
                    """
                        CREATE TABLE IF NOT EXISTS notification (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            send INTEGER NOT NULL,
                            datetime TIMESTAMP NOT NULL
                        );
                    """
                )

                check_data = cur.execute("SELECT id FROM notification LIMIT 1;").fetchone()
                if check_data is None:
                    datetime = strftime("%Y-%m-%d %H:%M:%S")
                    cur.execute(
                        "INSERT INTO notification (id, send, datetime) VALUES (NULL, ?, ?);",
                        (0, datetime)
                    )

                self.con.commit()

        except sqlite3.Error as error:
            logger.error(f"Error [create section]: {error}")


    def insert(self, voltage, capacity, status):
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
                        return

                # https://stackoverflow.com/a/32339569/6539270
                con.execute(
                    "INSERT INTO battery VALUES (NULL, ?, ?, ?, ?);",
                    (voltage, capacity, status, datetime),
                )
                self.con.commit()

        except Exception as error:
            logger.error(f"Error [insert section]: {error}")


    def execute(self, query, *args):
        try:
            with self.con as con:
                cur = con.cursor()

                res = cur.execute(query, args).fetchone()

                return res

        except sqlite3.Error as error:
            logger.error(f"Error [execute section] {query}\n Error: {error}")


    def drop_table(self):
        try:
            with self.con as con:
                cur = con.cursor()
                cur.execute("DROP TABLE battery;")
                cur.execute("DROP TABLE notification;")
                self.con.commit()

        except Exception as error:
            logger.error(f"Error [drop section]: {error}")
