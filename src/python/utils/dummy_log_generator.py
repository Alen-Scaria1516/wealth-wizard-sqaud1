import random
import string
import json
from bson import json_util   # comes with pymongo
from datetime import datetime, timedelta
import os


#Dummy data generation code for passwordReset
def generate_dummy_passwordReset_logs(num_users=100):
    logs = []
    base_time = datetime.now()
    for i in range(num_users):
        email = f"username{i}@dummy.com"
        token = ''.join(random.choices(string.digits, k=6))  # fixed token per user
        
        time = base_time + timedelta(seconds=i*30)
        
        # Log token generation
        logs.append({
            "email_id": email,
            "category" : "PASSWORD_RESET",
            "action": "TOKEN_GENERATED",
            "details": {"token": token},
            "timestamp": time   
        })
        
        successful = False
        
        for attempt in range(1, 4):  # max 3 attempts
            time += timedelta(seconds=20)

            if not successful and random.random() < 0.4:  # ~40% chance to succeed
                successful = True
                status = True
                input_token = token
            else:
                status = False
                input_token = ''.join(random.choices(string.digits, k=6))
                
            logs.append({
                "email_id": email,
                "category" : "PASSWORD_RESET",
                "action": "ATTEMPT",
                "details": {
                    "attempt_number": attempt,
                    "input_token": input_token,
                    "status": status
                },
                "timestamp": time   
            })
            if successful:
                    break

    return logs


# ---------------- MASTER FUNCTION ---------------- #
def generate_dummy_logs(n=100):
    """Generate combined dummy logs for all usecases."""
    logs = []
    # logs.extend(generate_dummy_registration_logs(n//4))
    # logs.extend(generate_dummy_login_logs(n//4))
    logs.extend(generate_dummy_passwordReset_logs(n//4))
    # logs.extend(generate_dummy_verification_logs(n//4))
    return logs


# ---------------- EXECUTION ---------------- #
if __name__ == "__main__":
    dummy_logs = generate_dummy_logs(200)   # generate 200 logs
    
    file_name = "dummy_logs.txt"
    
    with open(file_name, "w") as f:
        f.write(json_util.dumps(dummy_logs, indent=2))  # keeps datetime JSON-compatible
    print("✅ Dummy logs generated and saved to dummy_logs.txt")
    
    #insert into MongoDB only once
    # mongoimport --db User_logs --collection logs --file ./datafiles/dummy_logs.txt --jsonArray
