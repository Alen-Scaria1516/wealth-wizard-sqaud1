from utils.code_generation import generate_and_store_token 
from utils.code_validation import code_validation
from utils.send_email import send_verification_email
def email_verification(connection):
    flag = True
    cursor = connection.cursor()
    
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
            send_verification_email(email_id, token_for_email, code=1)

            # Allow up to 3 attempts
            for token_attempt in range(3):
                input_token = input("Enter your verification token: ")

                # Validate the token
                status = code_validation(email_id, input_token, connection)

                if status == True:
                    print("Verified")
                    break
                else:
                    remaining = 2 - token_attempt
                    if remaining >= 1:
                        print(f"Invalid token. You have {remaining} attempt(s) left. Please try again.")
                    else:
                        print("Verification failed. Please restart the process.")
