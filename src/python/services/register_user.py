import oracledb
from datetime import datetime
import re
import bcrypt
from getpass import getpass
from utils.send_email import send_registration_email
from services.email_verification import email_verification

#strong password
def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )
    
#registration
def register_user(connection):
    cursor = connection.cursor()
    
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    #existing user from stored procedure
    email_count = cursor.var(oracledb.NUMBER)
    cursor.callproc("check_user_email", [email, email_count])
    if email_count.getvalue() > 0:
        print("User already registered. Please login.")
        return
    age = int(input("Enter your age: "))
    print("\nPassword requirements:")
    print("- At least 8 characters")
    print("- At least one uppercase letter")
    print("- At least one lowercase letter")
    print("- At least one number")
    print("- At least one special character (!@#$%^&* etc.)\n")

    #weak password
    while True:
        print("\nEnter your password (input will be hidden):")
        password = getpass("Password: ")

        print("Re-enter your password (input will be hidden):")
        confirm_password = getpass("Confirm Password: ")
        print(type(password))

        if password != confirm_password:
            print("Passwords do not match. Try again.\n")
            continue

        if is_strong_password(password):
            break
        else:
            print("Weak password. Please follow the rules.\n")
    
    print(type(password))
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
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
        # verify email
        email_verification(connection, email)

    except oracledb.IntegrityError:
        print("Error: Email already exists.")
    except Exception as e:
        print("An error occurred:", e)
        
    cursor.close()
    return 