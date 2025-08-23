from getpass import getpass
import re
import bcrypt

#strong password
def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )
    
def get_password():
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
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return hashed_password