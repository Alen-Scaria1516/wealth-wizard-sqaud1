import oracledb
from datetime import datetime
from utils.send_email import send_registration_email
from utils.password import get_password
from services.email_verification import email_verification

    
#registration
def register_user(connection):
    cursor = connection.cursor()
    
    success = 0
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    #existing user from stored procedure
    email_count = cursor.var(oracledb.NUMBER)
    cursor.callproc("check_user_email", [email, email_count])
    if email_count.getvalue() > 0:
        print("User already registered. Please login.")
        cursor.close()
        return
    age = int(input("Enter your age: "))
    # print(type(password))
    hashed_password = get_password()
    
    #user_id
    cursor.execute("SELECT 'U' || LPAD(user_seq.NEXTVAL, 3, '0') FROM dual")
    user_id = cursor.fetchone()[0]
    #reg_id
    cursor.execute("SELECT 'R' || LPAD(user_profile_seq.NEXTVAL, 3, '0') FROM dual")
    reg_id = cursor.fetchone()[0]
    try:
        # Insert into Users
        cursor.execute("""
            INSERT INTO Users (User_ID, Email_ID, Password, last_modified)
            VALUES (:1, :2, :3, :4)
        """, (user_id, email, hashed_password, datetime.now()))

        # Insert into user_details
        cursor.execute("""
            INSERT INTO user_details (reg_id, user_id, name, age)
            VALUES (:1, :2, :3, :4)
        """, (reg_id, user_id, name, age))

        connection.commit()
        print("Registration successful!")
        print(f"Your User ID: {user_id}, Registration ID: {reg_id}")

        # send email
        send_registration_email(email, user_id, reg_id)
        success = 1
        print("Email Verification")
        email_verification(connection, email)

    except oracledb.IntegrityError:
        print("Error: Email already exists.")
    except Exception as e:
        print("An error occurred:", e)
        
    cursor.close()
    return success