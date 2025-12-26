import os
import smtplib
from email.message import EmailMessage

from app.logger import logger

# TODO: In production, use Pydantic Settings or python-dotenv, yb
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465


def send_birthday_email(friend_name: str, days_until: int):
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        logger.warn("⚠️ Email credentials not set. Skipping email.")
        return

    msg = EmailMessage()

    if days_until == 0:
        subject = f"🎉 It's {friend_name}'s Birthday Today!"
        body = f"Don't forget to wish {friend_name} a happy birthday today!"
    else:
        subject = f"🎂 Upcoming Birthday: {friend_name}"
        body = f"{friend_name}'s birthday is in {days_until} days."

    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS  # Sending to myself rn # TODO change later
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        logger.info(f"Email sent for {friend_name}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
