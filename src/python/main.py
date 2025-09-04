from services import register_user, login_user, forget_password, email_verification, admin
from database.connection import get_connection
from database.mongo_connection import get_mongo_connection

def main_menu():
    connection = get_connection()
    mongo_connection = get_mongo_connection()
    while True:
        print("\n=== Wealth Wizard Menu ===")
        print("1. Register")
        print("2. Login")
        print("3. Admin")
        print("4. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            successful_registration = register_user(connection)
            if successful_registration == 1: 
                print("\n Login ")
                login_user(connection, mongo_connection)
        elif choice == "2":
            login_user(connection, mongo_connection)
        elif choice == "3":
            admin.admin_verification_stats()
        elif choice == "4":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Try again.")
    
    connection.close()

main_menu()