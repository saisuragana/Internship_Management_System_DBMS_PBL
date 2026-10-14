import os

import mysql.connector


def get_db_connection():
    """Create a MySQL connection from environment configuration.

    Local development defaults to a database named internship_management.
    Set DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, and optionally DB_PORT for
    hosted MySQL. Never commit real credentials to source control.
    """
    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "Dattu9553"),
        "database": os.getenv("DB_NAME", "internship_management"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "connection_timeout": 10,
    }
    if not config["password"]:
        raise RuntimeError(
            "DB_PASSWORD is not set. Set it in your local environment or hosting dashboard."
        )
    # Optional CA certificate path for managed MySQL providers that require TLS.
    ssl_ca = os.getenv("DB_SSL_CA")
    if ssl_ca:
        config["ssl_ca"] = ssl_ca
        config["ssl_verify_cert"] = True
    return mysql.connector.connect(**config)
