from datetime import datetime, timedelta
from utils.code_generation import generate_and_store_token
from utils.send_email import send_verification_email
from utils.password import get_password
import oracledb
from utils.log_generation import log_to_mongo

def forget_password(connection, mongo_connection):
    try:
        cursor = connection.cursor()
        
        client = mongo_connection
        db = client["User_logs"]
        logs_collection = db["logs"]
        
        email = input('Enter email :')
        cursor.execute('SELECT User_ID FROM USERS WHERE Email_ID = :email', {"email" : email})
        row = cursor.fetchone()
        
        if not row:
            print('Email Not Found. Try Again.')
            return forget_password(connection, mongo_connection)

        token = generate_and_store_token(email, connection)
        log_to_mongo(logs_collection, email, "PASSWORD_RESET","TOKEN_GENERATED", {"token": token})
        
        send_verification_email(email, token, code=2)
        # print(f"\n[DEBUG] Token sent to email (showing in terminal for now): {token}")
        
        cursor.execute("""
            SELECT token, last_modified
            FROM Users
            WHERE email_id = :email_id
        """, {"email_id": email})
        
        # row = cursor.fetchone()
        
        # db_token, time_generated = row
        
        for token_attempt in range(2):  
            #Getting token from user 
            entered_token = input("Enter the token: ")  
            
            valid_token = cursor.callfunc("CodeValidationForPassword", oracledb.NUMBER, [email, entered_token] )
            log_to_mongo(
                    logs_collection,
                    email, "PASSWORD_RESET",
                    "ATTEMPT",
                    {"attempt_number": token_attempt+1, "input_token": token, "status": bool(valid_token)}
                )
            
            if valid_token ==0 :
                remaining = 1 - token_attempt
                if remaining >= 1:
                    print("Invalid token. Password reset failed. Please Try Again.")
                else:
                    print("Error: Password Reset denied.")
            else :
                new_password = get_password()
                cursor.execute(
                    "UPDATE Users SET password = :password, last_modified = CURRENT_TIMESTAMP WHERE Email_ID = :email", {"password" : new_password, "email" : email})
                connection.commit()
                
                print("Password reset successful. Please Try Login.\n")
                break
    except Exception as e:
        print('Error Occured :', e)
    finally:
        cursor.close()
    return