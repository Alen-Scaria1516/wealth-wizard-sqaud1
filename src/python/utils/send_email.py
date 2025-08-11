import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()
sender_email = os.getenv("sender_email")
app_password = os.getenv("app_password")

def send_verification_email(email_id, token_for_email):
    message = MIMEText(f"Your code for verification is: {token_for_email}")
    message["Subject"] = "Verify Your Email"
    message["From"] = sender_email
    message["To"] = email_id
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(message)

    print("Email sent successfully")