# Gmail Email Monitor Setup Guide

This guide will help you set up automated phone call notifications for important emails from Trinity College Dublin.

## Overview

The system monitors your Gmail inbox for emails from:
- `postgrad.admin@dental.tcd.ie`
- `Amy.Fisher@dental.tcd.ie`

When an email arrives from these senders, you'll receive an immediate phone call with details about the email.

---

## Prerequisites

- Python 3.7 or higher
- A Gmail account
- A phone number to receive calls
- A Twilio account (for making phone calls)

---

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or if you're using Python 3 specifically:
```bash
pip3 install -r requirements.txt
```

---

## Step 2: Set Up Gmail API Access

### 2.1 Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
   - Click "Select a project" at the top
   - Click "New Project"
   - Name it something like "Gmail Monitor"
   - Click "Create"

3. Enable the Gmail API:
   - In the search bar, type "Gmail API"
   - Click on "Gmail API"
   - Click "Enable"

### 2.2 Create OAuth Credentials

1. In Google Cloud Console, go to "Credentials" (in the left sidebar)
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: Select "External"
   - Click "Create"
   - Fill in App name: "Gmail Monitor"
   - User support email: (your email)
   - Developer contact: (your email)
   - Click "Save and Continue"
   - Skip "Scopes" (click "Save and Continue")
   - Add your email as a test user
   - Click "Save and Continue"

4. Now create the OAuth client ID:
   - Application type: "Desktop app"
   - Name: "Gmail Monitor Desktop"
   - Click "Create"

5. Download the credentials:
   - Click the download icon (⬇) next to your newly created OAuth client
   - Save the file as `credentials.json` in this project directory

### 2.3 Verify credentials.json

Make sure the `credentials.json` file is in the same directory as `gmail_monitor.py`.

---

## Step 3: Set Up Twilio (Phone Calls)

### 3.1 Create Twilio Account

1. Go to [Twilio Sign Up](https://www.twilio.com/try-twilio)
2. Create a free account
3. Verify your email and phone number

### 3.2 Get a Twilio Phone Number

1. In the Twilio Console, go to "Phone Numbers" → "Manage" → "Buy a number"
2. Choose a number from your country (make sure it has "Voice" capability)
3. Purchase the number (free trial gives you $15 credit)

### 3.3 Get Your Twilio Credentials

1. From the [Twilio Console Dashboard](https://console.twilio.com/):
   - Find your **Account SID**
   - Find your **Auth Token** (click to reveal)
   - Note your **Twilio Phone Number** (from Phone Numbers section)

---

## Step 4: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your actual credentials:
```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
YOUR_PHONE_NUMBER=+1234567890

# Email Monitoring Configuration
SENDER_EMAILS=postgrad.admin@dental.tcd.ie,Amy.Fisher@dental.tcd.ie
CHECK_INTERVAL_SECONDS=60

# Optional: Custom message for phone call
CALL_MESSAGE=You have received an important email from Trinity College Dublin. Please check your inbox immediately.
```

**Important Notes:**
- Phone numbers must be in E.164 format (e.g., +353871234567 for Ireland)
- `TWILIO_PHONE_NUMBER` is the number you purchased from Twilio
- `YOUR_PHONE_NUMBER` is your personal phone number where you want to receive calls
- If using Twilio trial account, you must verify your personal phone number in Twilio first

---

## Step 5: Run the Monitor

### First Run (Authentication)

The first time you run the script, it will open a browser window to authenticate with Gmail:

```bash
python3 gmail_monitor.py
```

1. A browser window will open
2. Select your Gmail account
3. Click "Advanced" → "Go to Gmail Monitor (unsafe)" (it's safe, it's your own app)
4. Click "Allow" to grant permissions
5. The browser will show "The authentication flow has completed"
6. Return to your terminal

The script will create a `token.pickle` file to remember your authentication.

### Normal Operation

After the first run, simply execute:

```bash
python3 gmail_monitor.py
```

You should see output like:
```
============================================================
Gmail Email Monitor - Starting
============================================================
Monitoring emails from: postgrad.admin@dental.tcd.ie, Amy.Fisher@dental.tcd.ie
Check interval: 60 seconds
Phone notifications to: +353871234567
============================================================

✓ Gmail API authenticated successfully
✓ Twilio client initialized successfully

✓ Monitoring started! Waiting for important emails...

[2026-01-19 14:30:00] Checking for new emails...
  No new emails.
```

---

## Step 6: Keep It Running

### Option A: Run in Terminal (Temporary)

Just keep the terminal window open. The script will check for emails every 60 seconds.

Press `Ctrl+C` to stop.

### Option B: Run in Background (Screen/Tmux)

Using `screen`:
```bash
screen -S gmail-monitor
python3 gmail_monitor.py
# Press Ctrl+A then D to detach
# Reattach with: screen -r gmail-monitor
```

Using `tmux`:
```bash
tmux new -s gmail-monitor
python3 gmail_monitor.py
# Press Ctrl+B then D to detach
# Reattach with: tmux attach -t gmail-monitor
```

### Option C: Run as a System Service (Permanent)

Create a systemd service file (Linux):

```bash
sudo nano /etc/systemd/system/gmail-monitor.service
```

Add this content (update paths):
```ini
[Unit]
Description=Gmail Email Monitor
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/claude-code-experiments
ExecStart=/usr/bin/python3 /path/to/claude-code-experiments/gmail_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable gmail-monitor
sudo systemctl start gmail-monitor
sudo systemctl status gmail-monitor
```

### Option D: Run on Server/Cloud

Deploy to a cloud server (AWS, DigitalOcean, etc.) so it runs 24/7 even when your computer is off.

---

## What Happens When You Get an Email

1. The script detects a new unread email from the specified senders
2. You immediately receive a phone call on your phone
3. An automated voice message tells you:
   - You have received an important email
   - The sender's email address
   - The email subject line
   - Repeats the message

4. The script logs the email details to the console
5. The email ID is saved so you don't get duplicate notifications

---

## Testing

### Test with a Real Email

1. Start the monitor: `python3 gmail_monitor.py`
2. Send yourself a test email from `postgrad.admin@dental.tcd.ie` (or ask someone with that account to send you one)
3. Wait up to 60 seconds (the check interval)
4. You should receive a phone call!

### Check Logs

The script prints detailed logs to the console. You'll see:
- When it checks for emails
- When new emails are detected
- When phone calls are made
- Any errors

---

## Troubleshooting

### "credentials.json not found"
- Make sure you downloaded the OAuth credentials from Google Cloud Console
- Place the file in the same directory as `gmail_monitor.py`

### "Missing Twilio configuration"
- Check your `.env` file exists and has all required variables
- Make sure there are no typos in variable names

### "Unable to make call"
- Verify your Twilio phone numbers are in E.164 format (+country code)
- If using trial account, verify your phone number in Twilio console
- Check your Twilio account balance

### Not detecting emails
- Make sure the emails are unread
- Check the sender email addresses match exactly
- Try checking your Gmail manually to confirm the email arrived
- Look at the console logs for any errors

### Gmail authentication issues
- Delete `token.pickle` and run again to re-authenticate
- Make sure you added your email as a test user in OAuth consent screen
- Check that Gmail API is enabled in Google Cloud Console

---

## Security Notes

1. **Keep credentials.json secure** - Contains OAuth client secrets
2. **Keep .env secure** - Contains Twilio credentials and API keys
3. **Never commit credentials** - They're already in `.gitignore`
4. **Use environment-specific credentials** - Don't share production credentials

---

## Customization

### Change Check Interval

Edit `.env`:
```bash
CHECK_INTERVAL_SECONDS=30  # Check every 30 seconds instead of 60
```

### Change Call Message

Edit `.env`:
```bash
CALL_MESSAGE=Urgent email received! Check your inbox now.
```

### Monitor Different Senders

Edit `.env`:
```bash
SENDER_EMAILS=sender1@example.com,sender2@example.com,sender3@example.com
```

### Add Subject Filtering

Edit `gmail_monitor.py` and modify the query in `check_for_emails()`:
```python
query = ' OR '.join(query_parts)
query += ' is:unread subject:"interview" OR subject:"acceptance"'  # Example
```

---

## Cost Estimate

- **Gmail API**: Free (within generous quota limits)
- **Twilio Phone Calls**: ~$0.01-0.02 per call (varies by country)
- **Twilio Trial Account**: $15 free credit

For occasional important emails, this should cost less than $1/month.

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the console logs for error messages
3. Verify all credentials are correct
4. Test your Gmail API and Twilio setups independently

---

## Files Overview

- `gmail_monitor.py` - Main monitoring script
- `requirements.txt` - Python dependencies
- `.env` - Your configuration (create from `.env.example`)
- `credentials.json` - Gmail OAuth credentials (download from Google Cloud)
- `token.pickle` - Gmail authentication token (auto-generated)
- `notified_emails.json` - Tracks emails you've been notified about (auto-generated)

---

## Quick Start Checklist

- [ ] Install Python dependencies
- [ ] Set up Gmail API and download credentials.json
- [ ] Create Twilio account and get phone number
- [ ] Copy .env.example to .env and fill in credentials
- [ ] Run `python3 gmail_monitor.py` for first-time authentication
- [ ] Test with a real email
- [ ] Set up background running (screen/tmux/systemd)

---

Good luck! You won't miss that important email. 🎯
