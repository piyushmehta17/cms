# db.py
import mysql.connector
from config import config

def get_db_connection(database=config.DB_NAME):
    return mysql.connector.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=database if database else None  # Allow optional database parameter
    )