"""Alert delivery. Email (SMTP) is the only channel in v1; the Notifier
interface makes it straightforward to add Telegram/Twilio/etc later."""

import os
import smtplib
from abc import ABC, abstractmethod
from email.message import EmailMessage

from .rules import FiredRule


class Notifier(ABC):
    @abstractmethod
    def send(self, subject: str, body: str) -> None:
        ...


class EmailNotifier(Notifier):
    def __init__(self):
        self.host = os.environ.get("SMTP_HOST")
        self.port = int(os.environ.get("SMTP_PORT", "587"))
        self.username = os.environ.get("SMTP_USERNAME")
        self.password = os.environ.get("SMTP_PASSWORD")
        self.from_email = os.environ.get("ALERT_FROM_EMAIL", self.username)
        self.to_email = os.environ.get("ALERT_TO_EMAIL", self.username)

    def is_configured(self) -> bool:
        return bool(self.host and self.username and self.password and self.to_email)

    def send(self, subject: str, body: str) -> None:
        if not self.is_configured():
            raise RuntimeError(
                "Email alerts are not configured. Set SMTP_HOST/SMTP_USERNAME/"
                "SMTP_PASSWORD/ALERT_TO_EMAIL in your .env (see .env.example)."
            )
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = self.to_email
        msg.set_content(body)

        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)


def format_alert(product_name: str, url: str, fired: list[FiredRule]) -> tuple[str, str]:
    name = product_name or url
    subject = f"[Price Tracker] {name}: {'; '.join(r.rule for r in fired)}"
    lines = [f"Price alert for: {name}", url, ""]
    for r in fired:
        lines.append(f"- {r.message}")
    body = "\n".join(lines)
    return subject, body


def send_alert(notifier: Notifier, product_name: str, url: str, fired: list[FiredRule]) -> None:
    subject, body = format_alert(product_name, url, fired)
    notifier.send(subject, body)
