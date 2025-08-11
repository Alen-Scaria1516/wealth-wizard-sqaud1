from datetime import datetime, timedelta
def code_validation(email_id, inputToken, connection):
    cursor = connection.cursor()
    cursor.execute(
        "Select token, last_modified from users WHERE email_id = :email_id",
        {"email_id": email_id}
    )
    status = False
    dbToken, timeGenerated = cursor.fetchone()
    if dbToken == inputToken and datetime.now() - timeGenerated < timedelta(minutes = 10):
        print("User verified successfully")
        cursor.execute(
        "UPDATE Users SET is_verified = 1, last_modified = :time_now WHERE email_id = :email_id",
        {"time_now": datetime.now(), "email_id": email_id})
        connection.commit()
        status = True

    else:
        print("Incorrect token or token expired, verify again.")
        status = False


    #cursor.execute("SELECT * FROM Users WHERE email_id = :email_id", {"email_id": email_id})
    # for row in cursor:
    #     print(row)

    # Close connection
    cursor.close()
    return status