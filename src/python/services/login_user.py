import bcrypt
import getpass

def login_user(connection):
    email = input("Enter your email: ").strip()

    try:
        cur = connection.cursor()

        # Check if user exists by email first
        cur.execute("""
            SELECT User_ID, Password, is_Verified, is_loggedIn
            FROM USERS
            WHERE Email_ID = :email
        """, {"email": email})

        user = cur.fetchone()

        if not user:
            print("Error: Please register before logging in.")
            return  # Stop here if email not found

        user_id, stored_password, is_verified, is_loggedin = user
        # print(type(stored_password))
        
        if is_verified != 1:
            print("Error: Please verify your account before logging in.")
            return
        
        for attempt in range(3):
            pw_try = getpass.getpass("Enter your password: ").strip()

            ok = bcrypt.checkpw(pw_try.encode(), stored_password.encode())

            if ok:
                # Password correct
                if is_loggedin == 1:
                    print("Error: User already logged in.")
                    return

                cur.execute("""
                    UPDATE USERS
                    SET is_loggedIn = 1,
                        last_modified = SYSTIMESTAMP
                    WHERE User_ID = :user_id
                """, {"user_id": user_id})
                connection.commit()
                print("Login successful! Redirecting to dashboard...")
                return (user_id, email)

            else:
                remaining = 2 - attempt
                if remaining >= 1:
                    print("Error: Invalid password. Please try again.")
                else:
                    print("Error: Login denied.")
                    return None

    except Exception as e:
        print("Error during login:", e)
        return None
    finally:
        cur.close()
        
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