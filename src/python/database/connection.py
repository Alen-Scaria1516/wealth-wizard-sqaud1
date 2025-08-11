import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")


def get_connection():
    try:
        conn = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN
        )
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None

if __name__ =="__main__":
    connection = get_connection()
    if connection:    
        print("Connected to Oracle XE!")
        connection.close()