############---------------------#####################
#Dummy data generation code for verification
import random
import string
from datetime import datetime, timedelta

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
#########################################################################
# Generate 100 dummy logs
import json
from bson import json_util   # comes with pymongo
dummy_logs = generate_dummy_verification_logs(100)
# If you want JSON/TXT output that Mongo can also read back
with open("src\python\data_files/dummy_verification_logs.txt", "w") as f:
    f.write(json_util.dumps(dummy_logs, indent=2))   #handles datetime 

#push dummy logs to mongodb using terminal


###################################################################################
#Function for exporting logs from mongodb as text file 
import subprocess
import os

def export_verification_logs_to_txt(folder_path="src\python\data_files", file_name="verification_logs.txt"):
    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)

    # Full path for output file
    output_file = os.path.join(folder_path, file_name)

    cmd = [
        r"C:\Program Files\MongoDB\Tools\100\bin\mongoexport.exe",
        "--uri=mongodb://localhost:27017/User_logs",
        "--collection=logs",
        "--out", output_file,
        "--jsonArray"   # export as JSON array
    ]
    
    subprocess.run(cmd, check=True)
    print(f"Logs exported to {output_file}")


##################################################################


