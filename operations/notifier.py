import os
import smtplib

from email.message import EmailMessage


class EmailNotifier:

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.recipient = os.getenv("OPS_EMAIL_TO")

    def send(
        self,
        subject: str,
        body: str,
    ) -> None:

        if not all(
            [
                self.smtp_host,
                self.smtp_user,
                self.smtp_password,
                self.recipient,
            ]
        ):
            raise ValueError(
                "Email configuration is incomplete. "
                "Configure SMTP_HOST, SMTP_USER, SMTP_PASSWORD "
                "and OPS_EMAIL_TO."
            )

        message = EmailMessage()

        message["From"] = self.smtp_user
        message["To"] = self.recipient
        message["Subject"] = subject

        message.set_content(body)

        with smtplib.SMTP(
            self.smtp_host,
            self.smtp_port,
            timeout=30,
        ) as server:

            server.starttls()

            server.login(
                self.smtp_user,
                self.smtp_password,
            )

            server.send_message(message)