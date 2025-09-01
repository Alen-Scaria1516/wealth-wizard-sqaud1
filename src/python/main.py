from services import register_user, login_user, forget_password, email_verification, admin
from database.connection import get_connection
from database.mongo_connection import get_mongo_connection

def main_menu():
    connection = get_connection()
    mongo_connection = get_mongo_connection()
    
    while True:
        print("\n=== Wealth Wizard Menu ===")
        print("1. Login")
        print("2. Register")
        print('3. Forgot Password')
        print('4. Verification of Email')
        print("5. Admin Stats")
        print("6. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            login_user(connection)
        elif choice == "2":
            register_user(connection)
        elif choice == "3":
            forget_password(connection)    
        elif choice == "4":
            email_verification(connection,mongo_connection)
        elif choice == "5":
            admin.admin_verification_stats()
        elif choice == "6":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Try again.")
    connection.close()

main_menu()