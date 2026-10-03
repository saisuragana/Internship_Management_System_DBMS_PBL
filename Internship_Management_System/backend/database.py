import os

import mysql.connector


def get_db_connection():
    # Change the password below, or set the DB_PASSWORD environment
    # variable so the password is not stored in the code.
    connection = mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "Dattu9553"),
        database=os.environ.get("DB_NAME", "internship_management")
    )

    return connection
