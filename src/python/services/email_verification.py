from utils.code_generation import generate_and_store_token 
from utils.code_validation import code_validation
from utils.send_email import send_verification_email
from utils.log_generation import log_to_mongo
def email_verification(connection, mongo_connection):
    flag = True
    cursor = connection.cursor()
    
    client = mongo_connection
    db = client["User_logs"]
    logs_collection = db["logs"]
    
    email_id = input("Enter your Email ID : ")
    try:
        cursor.execute(
        "Select is_verified from users WHERE email_id = :email_id",
        {"email_id": email_id}
        )
        is_verified = cursor.fetchone()[0]
    except:
        print("\n No account found for the entered Email ID.")
        flag = False

    cursor.close()
    if (flag):
        if (is_verified == 1):
            print("\nUser is already verified.")
        else:
            # Generate and send token
            token_for_email = generate_and_store_token(email_id, connection)
            log_to_mongo(logs_collection, email_id, "TOKEN_GENERATED", {"token": token_for_email})
            send_verification_email(email_id, token_for_email, code=1)

            # Allow up to 3 attempts
            for token_attempt in range(3):
                input_token = input("Enter your verification token sent to your email : ")

                # Validate the token
                status = code_validation(email_id, input_token, connection)
                log_to_mongo(
                    logs_collection,
                    email_id,
                    "ATTEMPT",
                    {"attempt_number": token_attempt+1, "input_token": input_token, "status": status}
                )

                if status == True:
                    print("Verified")
                    break
                else:
                    remaining = 2 - token_attempt
                    if remaining >= 1:
                        print(f"Invalid token. You have {remaining} attempt(s) left. Please try again.")
                    else:
                        print("Verification failed. Please restart the process.")
