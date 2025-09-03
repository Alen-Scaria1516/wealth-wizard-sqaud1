from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv("mongo_connection_string")

def get_mongo_connection():
    try:
        client = MongoClient(connection_string)
        return client
    except Exception as e:
        print("MongoDb connection failed:", e)
        return None
    
if __name__ =="__main__":
    mongo_connection = get_mongo_connection()
    if mongo_connection:    
        print("Connected to mongodb")
        mongo_connection.close()