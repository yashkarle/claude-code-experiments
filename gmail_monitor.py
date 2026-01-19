#!/usr/bin/env python3
"""
Gmail Email Monitor with Phone Call Notifications
Monitors Gmail for important emails and triggers phone calls via Twilio
"""

import os
import time
import json
import pickle
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from twilio.rest import Client as TwilioClient

# Load environment variables
load_dotenv()

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Configuration
SENDER_EMAILS = os.getenv('SENDER_EMAILS', '').split(',')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL_SECONDS', 60))
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
YOUR_PHONE_NUMBER = os.getenv('YOUR_PHONE_NUMBER')
CALL_MESSAGE = os.getenv('CALL_MESSAGE',
    'You have received an important email. Please check your inbox immediately.')

# File to track notified emails
NOTIFIED_EMAILS_FILE = 'notified_emails.json'


class GmailMonitor:
    def __init__(self):
        self.service = None
        self.twilio_client = None
        self.notified_emails = self.load_notified_emails()

    def load_notified_emails(self):
        """Load the list of already notified email IDs"""
        if Path(NOTIFIED_EMAILS_FILE).exists():
            with open(NOTIFIED_EMAILS_FILE, 'r') as f:
                return set(json.load(f))
        return set()

    def save_notified_emails(self):
        """Save the list of notified email IDs"""
        with open(NOTIFIED_EMAILS_FILE, 'w') as f:
            json.dump(list(self.notified_emails), f)

    def authenticate_gmail(self):
        """Authenticate with Gmail API"""
        creds = None
        token_file = 'token.pickle'

        # Load existing credentials
        if Path(token_file).exists():
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not Path('credentials.json').exists():
                    raise FileNotFoundError(
                        "credentials.json not found. Please follow setup instructions."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for future use
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)
        print("✓ Gmail API authenticated successfully")

    def setup_twilio(self):
        """Initialize Twilio client"""
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, YOUR_PHONE_NUMBER]):
            raise ValueError(
                "Missing Twilio configuration. Please set all required environment variables."
            )

        self.twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print("✓ Twilio client initialized successfully")

    def make_phone_call(self, email_info):
        """Make a phone call via Twilio"""
        try:
            # Create TwiML for the call message
            twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{CALL_MESSAGE}</Say>
    <Pause length="1"/>
    <Say voice="alice">From: {email_info['from']}</Say>
    <Say voice="alice">Subject: {email_info['subject']}</Say>
    <Pause length="1"/>
    <Say voice="alice">This message will repeat.</Say>
    <Pause length="2"/>
    <Say voice="alice">{CALL_MESSAGE}</Say>
</Response>'''

            call = self.twilio_client.calls.create(
                twiml=twiml,
                to=YOUR_PHONE_NUMBER,
                from_=TWILIO_PHONE_NUMBER
            )

            print(f"✓ Phone call initiated! Call SID: {call.sid}")
            return True

        except Exception as e:
            print(f"✗ Error making phone call: {e}")
            return False

    def get_email_details(self, message_id):
        """Retrieve email details"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()

            headers = {h['name']: h['value'] for h in message['payload']['headers']}

            return {
                'id': message_id,
                'from': headers.get('From', 'Unknown'),
                'subject': headers.get('Subject', 'No Subject'),
                'date': headers.get('Date', 'Unknown'),
                'snippet': message.get('snippet', '')
            }
        except Exception as e:
            print(f"✗ Error getting email details: {e}")
            return None

    def check_for_emails(self):
        """Check for new emails from specified senders"""
        try:
            # Build query for sender emails
            query_parts = [f'from:{email.strip()}' for email in SENDER_EMAILS if email.strip()]
            query = ' OR '.join(query_parts)
            query += ' is:unread'  # Only check unread emails

            # Search for matching emails
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()

            messages = results.get('messages', [])

            new_emails = []
            for msg in messages:
                msg_id = msg['id']
                if msg_id not in self.notified_emails:
                    email_info = self.get_email_details(msg_id)
                    if email_info:
                        new_emails.append(email_info)
                        self.notified_emails.add(msg_id)

            return new_emails

        except Exception as e:
            print(f"✗ Error checking emails: {e}")
            return []

    def process_new_emails(self, emails):
        """Process new emails and send notifications"""
        for email in emails:
            print(f"\n{'='*60}")
            print(f"🚨 NEW IMPORTANT EMAIL DETECTED!")
            print(f"{'='*60}")
            print(f"From: {email['from']}")
            print(f"Subject: {email['subject']}")
            print(f"Date: {email['date']}")
            print(f"Preview: {email['snippet'][:100]}...")
            print(f"{'='*60}\n")

            # Make phone call
            print("📞 Initiating phone call...")
            success = self.make_phone_call(email)

            if success:
                print("✓ Notification sent successfully!")
            else:
                print("✗ Failed to send notification")

            # Save updated notified emails list
            self.save_notified_emails()

    def run(self):
        """Main monitoring loop"""
        print("\n" + "="*60)
        print("Gmail Email Monitor - Starting")
        print("="*60)
        print(f"Monitoring emails from: {', '.join(SENDER_EMAILS)}")
        print(f"Check interval: {CHECK_INTERVAL} seconds")
        print(f"Phone notifications to: {YOUR_PHONE_NUMBER}")
        print("="*60 + "\n")

        # Initialize services
        self.authenticate_gmail()
        self.setup_twilio()

        print("\n✓ Monitoring started! Waiting for important emails...\n")

        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Checking for new emails...")

                new_emails = self.check_for_emails()

                if new_emails:
                    self.process_new_emails(new_emails)
                else:
                    print("  No new emails.")

                time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n\n⚠ Monitoring stopped by user")
            self.save_notified_emails()
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
            self.save_notified_emails()
            raise


def main():
    """Entry point"""
    try:
        monitor = GmailMonitor()
        monitor.run()
    except FileNotFoundError as e:
        print(f"\n✗ Setup Error: {e}")
        print("\nPlease complete the setup steps in SETUP.md first.")
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nPlease check your .env file configuration.")
    except Exception as e:
        print(f"\n✗ Fatal Error: {e}")
        raise


if __name__ == '__main__':
    main()
