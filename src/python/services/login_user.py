import bcrypt

def login_user(connection):
    email = input("Enter your email: ").strip()

    try:
        cur = connection.cursor()

        # Check if user exists by email first
        cur.execute("""
            SELECT User_ID, Password, is_Verified, is_loggedIn
            FROM SYSTEM.USERS
            WHERE Email_ID = :email
        """, {"email": email})

        user = cur.fetchone()

        if not user:
            print("Error: Please register before logging in.")
            return  # Stop here if email not found

        user_id, stored_password, is_verified, is_loggedin = user
        print(type(stored_password))

        password = input("Enter your password: ").strip()

        password_matches = False

        # Check if stored_password is hashed or plain text
        password_matches = bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))

        if password_matches:
            # Password correct
            if is_verified == 1:
                # Only allow login if user is verified
                # hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

                if is_loggedin == 1:
                    print("Error: User already logged in.")
                    return

                # Update hashed password, loggedIn flag, last_modified timestamp
                cur.execute("""
                    UPDATE SYSTEM.USERS
                    SET is_loggedIn = 1,
                        last_modified = SYSTIMESTAMP
                    WHERE User_ID = :user_id
                """, {"user_id": user_id})
                connection.commit()
                print("Login successful! Redirecting to dashboard...")
                return
            else:
                # User not verified, do not allow login
                print("Error: User not verified. Please verify your account before logging in.")
                return

        else:
            # Password incorrect
            print("Error: Invalid password.")
            return

    except Exception as e:
        # Friendly error message for unexpected issues
        print("Error: An unexpected error occurred during login. Please try again later.")
        # For debugging (optional): print(f"Debug info: {e}")
    finally:
        cur.close()
        
    return 
