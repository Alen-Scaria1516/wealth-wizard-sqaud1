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
            token_for_email = generate_and_store_token(email_id, connection)
            send_verification_email(email_id, token_for_email)
            print("\n")
            inputToken = input("Enter your verification token : ")
            status = code_validation(email_id, inputToken, connection)
            if status == True:
                print("Verified")
            if (status == False):
                #take to main menu.
                pass