from datetime import datetime

def log_to_mongo(mongo_collection, email_id, action, details=None):
    log_entry = {
        "email_id": email_id,
        "action": action,          # e.g., "TOKEN_GENERATED", "ATTEMPT", "VERIFIED"
        "details": details,        # optional info like token, attempt number, status
        "timestamp": datetime.now()
    }
    mongo_collection.insert_one(log_entry)