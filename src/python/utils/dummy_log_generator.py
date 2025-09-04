import random
import string
import json
from bson import json_util   # comes with pymongo
from datetime import datetime, timedelta
import os

#Dummy Log generation for Registration 
def generate_dummy_registration_logs(count=100):
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"]
    failure_reasons = ["invalid_email", "password_weak", "duplicate_email", "server_error"]
    logs = []
    base_time = datetime.now()

    def generate_random_email():
        username_length = random.randint(5, 12)
        username = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=username_length))
        domain = random.choice(domains)
        return f"{username}@{domain}"

    for i in range(count):
        email_id = generate_random_email()

        # Generate base timestamp for the attempt
        timestamp = base_time - timedelta(
            days=random.randint(0, 90),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        # Registration Attempt Log
        attempt_log = {
            "email_id": email_id,
            "category": "REGISTRATION",
            "action": "ATTEMPT",
            "details": {
                "attempt_number": 1,
                "ip_address": f"192.168.1.{random.randint(1, 255)}",
                "status": "initiated"
            },
            "timestamp": timestamp
        }

        # 90% chance of success
        if random.random() < 0.9:
            registered_timestamp = timestamp + timedelta(minutes=random.randint(1, 5))
            registered_log = {
                "email_id": email_id,
                "category": "REGISTRATION",
                "action": "REGISTERED",
                "details": {
                    "reg_id": f"R{str(i+1).zfill(3)}",
                    "age": random.randint(18, 75),
                    "status": "success"
                },
                "timestamp": registered_timestamp
            }
            logs.extend([attempt_log, registered_log])
        else:
            attempt_log["details"]["status"] = "failed"
            attempt_log["details"]["failure_reason"] = random.choice(failure_reasons)
            logs.append(attempt_log)

    return logs

#Dummy Log generation for Login 
def generate_token(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def random_timestamp(base_time, max_days_back=180):
    rand_days = random.randint(0, max_days_back)
    rand_seconds = random.randint(0, 86400)
    return base_time - timedelta(days=rand_days, seconds=rand_seconds)

def generate_dummy_login_logs(num_logs=100):
    reasons = ["invalid_password", "unregistered", "unverified"]
    logs = []
    base_time = datetime.now()

    for i in range(1, num_logs + 1):
        email_id = f"user{random.randint(100, 200)}@gmail.com"
        attempt_number = i
        status = random.choice([True, False])
        timestamp = random_timestamp(base_time)

        details = {
            "attempt_number": attempt_number,
            "status": status
        }

        if status:
            if random.random() < 0.8:
                details["token"] = generate_token()
            else:
                details["reason"] = "unverified"
                details["status"] = False
        else:
            details["reason"] = random.choice(reasons)

        logs.append({
            "email_id": email_id,
            "category": "LOGIN",
            "action": "LOGIN",
            "details": details,
            "timestamp": timestamp
        })

    return logs
    
#Dummy log generation code for passwordReset
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

#Dummy Log generation for Verification
def generate_dummy_verification_logs(num_users=100):
    logs = []
    base_time = datetime.now()

    for i in range(num_users):
        email = f"user{i}@dummy.com"
        token = ''.join(random.choices(string.digits, k=6))  # fixed token per user
        time = base_time + timedelta(seconds=i*30)

        # Log token generation
        logs.append({
            "email_id": email,
            "category": "VERIFICATION",
            "action": "TOKEN_GENERATED",
            "details": {"token": token},
            "timestamp": time   # store datetime object
        })

        verified = False
        for attempt in range(1, 4):  # max 3 attempts
            time += timedelta(seconds=20)

            if not verified and random.random() < 0.4:  # ~40% chance to succeed
                verified = True
                status = True
                input_token = token
            else:
                status = False
                input_token = ''.join(random.choices(string.digits, k=6))

            logs.append({
                "email_id": email,
                "category": "VERIFICATION",
                "action": "ATTEMPT",
                "details": {
                    "attempt_number": attempt,
                    "input_token": input_token,
                    "status": status
                },
                "timestamp": time   # still datetime, not string
            })

            if verified:
                break

    return logs


# ---------------- MASTER FUNCTION ---------------- #
def generate_dummy_logs(n=500):
    """Generate combined dummy logs for all usecases."""
    logs = []
    logs.extend(generate_dummy_registration_logs(n//4))
    logs.extend(generate_dummy_login_logs(n//4))
    logs.extend(generate_dummy_passwordReset_logs(n//4))
    logs.extend(generate_dummy_verification_logs(n//4))
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
