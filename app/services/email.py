"""Email service for sending notifications."""

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from typing import Optional

from app.core.config import settings


async def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
) -> None:
    """Send an email notification."""
    if not settings.EMAIL_ENABLED:
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.EMAIL_FROM
    message["To"] = to_email

    # Add plain text version
    message.attach(MIMEText(body, "plain"))

    # Add HTML version if provided
    if html_body:
        message.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)
    except Exception as e:
        # Log the error but don't raise it to prevent notification failure
        # from breaking the main flow
        print(f"Failed to send email: {e}") 