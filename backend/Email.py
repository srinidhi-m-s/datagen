import smtplib
from email.message import EmailMessage

SENDER_EMAIL = "datagenai26@gmail.com"
SENDER_PASSWORD = "hnxd cvsv syhr xzsl"


def send_notification_email(receiver_email: str, user_prompt: str, record_count: int = 0):
    """Send a notification email when data generation is complete."""
    msg = EmailMessage()
    msg["Subject"] = "DataGen AI — Your Data is Ready!"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    msg.set_content(
        f"Hello,\n\n"
        f"Your data generation request has completed successfully.\n\n"
        f"Prompt: {user_prompt}\n"
        f"Records generated: {record_count}\n\n"
        f"Head back to the DataGen AI platform to view and download your results.\n\n"
        f"Regards,\nDataGen AI"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)
