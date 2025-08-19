from datetime import datetime, timedelta
from utils.code_generation import generate_and_store_token
from utils.send_email import send_verification_email
import oracledb

def forget_password(connection):
    cursor = connection.cursor()
    
    email = input('Enter email :')
    cursor.execute('SELECT User_ID FROM USERS WHERE Email_ID = :email', {"email" : email})
    row = cursor.fetchone()
    
    if not row:
        print('Email Not Found.')
        cursor.close()
        return 

    token = generate_and_store_token(email, connection)
    
    send_verification_email(email, token)
    # print(f"\n[DEBUG] Token sent to email (showing in terminal for now): {token}")
    
    #Getting token from user 
    entered_token = input("Enter the token: ")
    
    cursor.execute("""
        SELECT token, last_modified
        FROM Users
        WHERE email_id = :email_id
    """, {"email_id": email})
    
    row = cursor.fetchone()
    
    db_token, time_generated = row
    
    valid_token = cursor.callfunc("CodeValidationForPassword", oracledb.NUMBER, [email, token] )
    
    if valid_token ==0 :
        print("Invalid token. Password reset failed.")
        cursor.close()
        connection.close()
        exit()
        
    else :
        new_password = input("Enter new password: ")
        cursor.execute(
            "UPDATE Users SET password = :password, last_modified = CURRENT_TIMESTAMP WHERE Email_ID = :email", {"password" : new_password, "email" : email})
        connection.commit()
        
        print("Password reset successful.")

    cursor.close()