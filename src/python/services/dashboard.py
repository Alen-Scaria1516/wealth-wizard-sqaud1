

def dashboard(connection, user_id):
    try:
        print("==== Available Options ===")
        print("1. Finance Check")
        print("2. Finance Check")
        print("3. Finance Check")
        print("4. Finance Check")
        print("5. Log Out")
        
        choice = input("Enter your choice :")
        if choice == "5":
            print("Logging Out")
            return True
    except KeyboardInterrupt:
        print("Logging Out")
        return True
        
        