import bcrypt
import getpass
from services.email_verification import email_verification
from services.forget_password import forget_password
from services.dashboard import dashboard
from utils.log_generation import log_to_mongo

def login_user(connection, mongo_connection):
    email = input("Enter your email: ").strip()

    try:
        cur = connection.cursor()
        
        client = mongo_connection
        db = client["User_logs"]
        logs_collection = db["logs"]
        
        # Check if user exists by email first
        cur.execute("""
            SELECT User_ID, Password, is_Verified, is_loggedIn
            FROM USERS
            WHERE Email_ID = :email
        """, {"email": email})

        user = cur.fetchone()

        if not user:
            print("Error: Not a Valid Email ID | Please register before logging in.")
            return  # Stop here if email not found

        user_id, stored_password, is_verified, is_loggedin = user
        # print(type(stored_password))
        
        if is_verified != 1:
            cur.close()
            print("Error: Please verify your account before logging in.")
            email_verification(connection,mongo_connection,email)
            return
        
        for attempt in range(3):
            pw_try = getpass.getpass("Enter your password: ").strip()

            ok = bcrypt.checkpw(pw_try.encode(), stored_password.encode())

            if ok:
                # Password correct
                if is_loggedin == 1:
                    print("Error: User already logged in.")
                    log_to_mongo(
                        mongo_collection=logs_collection,  # or your Mongo collection
                        email_id=email,
                        category="LOGIN",
                        action="LOGIN",
                        details={
                            "attempt_number": 1,
                            "status": True,
                            "reason": "already_logged_in"
                        }
                    )
                    return

                cur.execute("""
                    UPDATE USERS
                    SET is_loggedIn = 1,
                        last_modified = SYSTIMESTAMP
                    WHERE User_ID = :user_id
                """, {"user_id": user_id})
                connection.commit()
                print("Login successful! Redirecting to dashboard...")
                log_to_mongo(
                    mongo_collection=logs_collection,         # your MongoDB collection
                    email_id=email,
                    category="LOGIN",
                    action="LOGIN",
                    details={
                        "attempt_number": attempt + 1,
                        "status": True
                    }
                )
                logout = dashboard(connection, user_id)
                if logout : 
                    logout_user(connection, user_id)
                return (user_id, email)

            else:
                remaining = 2 - attempt
                if remaining >= 1:
                    print("Error: Invalid password. Try Forget Password or Please try again.")
                    log_to_mongo(
                        mongo_collection=logs_collection,
                        email_id=email,
                        category="LOGIN",
                        action="LOGIN",
                        details={
                            "attempt_number": attempt + 1,
                            "status": False,
                            "reason": "wrong_password"
                        }
                    )

                    print("1. Forgot Password")
                    print("Any other To Continue Attempt")
                    choice = input("Enter your choice: ")
                    if choice == "1":
                        #cur.close()
                        forget_password(connection, mongo_connection)
                        break
                    else : 
                        pass
                else:
                    print("Error: Login denied. ")
                    print("Exiting.")
                    return None

    except Exception as e:
        print("Error during login:", e)
        return None
    finally:
        # handling if cur is already closed or not
        try :
            cur.close()
        except Exception:
            pass
        
    return 

def logout_user(connection, user_id):
    """Logs out a user by clearing token and marking is_loggedIn = 0."""
    try:
        conn = connection
        cur = conn.cursor()
        cur.callproc("logout_user_proc", [user_id])
        conn.commit()
        print("Logged out.")
    except Exception as e:
        print("Error during logout:", e)