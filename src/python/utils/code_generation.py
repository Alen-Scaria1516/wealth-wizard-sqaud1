import random, string
from datetime import datetime
def generate_and_store_token(email_id, connection):
    token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    start_time = datetime.now()
    
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE Users
        SET token = :token, last_modified = :time_start
        WHERE email_id = :email_id
    """, {"token": token, "time_start": start_time, "email_id": email_id})
    connection.commit()
    cursor.close()

    return token
    