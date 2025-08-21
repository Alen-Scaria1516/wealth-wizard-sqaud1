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
    
def send_registration_email(receiver_email, user_id, reg_id):
    # # Email configuration
    # sender_email = "wealthwizard2k25@gmail.com"
    # app_password = "gdnc bxfg jtvy sapd"
    subject = "Wealth Wizard - Registration Successful"

    # Email body
    body = f"""
    Dear User,

    Congratulations! 

    Your registration with Wealth Wizard is successful.

    User ID: {user_id}
    Registration ID: {reg_id}

    Please keep these details safe for future reference.

    Regards,  
    Wealth Wizard Team
    """

    try:
        # Create email message
        msg = MIMEText(body, 'plain')
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        print(f"Confirmation email sent to {receiver_email}")
    except Exception as e:
        print("Failed to send email:", e)