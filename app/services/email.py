import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from email.mime.application import MIMEApplication
from typing import List, Optional


def send_email(
        to_email: str,
        subject: str,
        body: str,
        *,
        subtype: str = "html",
        attachments: Optional[List[str]] = None,
):
    """
    Sends an email using SMTP server configurations from settings.

    :param to_email: Recipient's email address.
    :param subject: Subject of the email.
    :param body: Body content of the email.
    :param subtype: MIME subtype ('html' or 'plain').
    :param attachments: List of file paths to attach to the email.
    """
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
    msg["To"] = to_email

    # Add body to email
    msg.attach(MIMEText(body, subtype))

    # Attach files if any
    if attachments:
        for file_path in attachments:
            try:
                with open(file_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=file_path)
                part["Content-Disposition"] = f'attachment; filename="{file_path}"'
                msg.attach(part)
            except Exception as e:
                print(f"Failed to attach file {file_path}: {e}")

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            print(f"Email sent successfully to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        raise e
