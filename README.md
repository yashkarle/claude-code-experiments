# Gmail Email Monitor with Phone Notifications

Never miss an important email again! This system monitors your Gmail inbox for critical emails and immediately calls your phone when they arrive.

## What It Does

- Monitors Gmail for emails from specific senders
- Sends instant phone call notifications when important emails arrive
- Provides email details via automated voice message
- Tracks notified emails to prevent duplicates

## Current Configuration

Monitoring emails from:
- `postgrad.admin@dental.tcd.ie`
- `Amy.Fisher@dental.tcd.ie`

## Quick Start

1. See **[SETUP.md](SETUP.md)** for complete setup instructions
2. Install dependencies: `pip install -r requirements.txt`
3. Configure Gmail API and Twilio credentials
4. Run: `python3 gmail_monitor.py`

## Features

- Real-time Gmail monitoring via Gmail API
- Phone call notifications via Twilio
- Customizable check intervals
- Persistent tracking of notified emails
- Detailed logging and error handling
- Easy configuration via `.env` file

## Requirements

- Python 3.7+
- Gmail account with API access
- Twilio account for phone calls
- Phone number to receive notifications

## Documentation

- [Complete Setup Guide](SETUP.md) - Step-by-step instructions
- [Environment Configuration](.env.example) - Configuration template

## Cost

- Gmail API: Free
- Twilio calls: ~$0.01-0.02 per call
- Total: Less than $1/month for occasional important emails

## Files

- `gmail_monitor.py` - Main monitoring script
- `SETUP.md` - Detailed setup instructions
- `requirements.txt` - Python dependencies
- `.env.example` - Configuration template

---

Never miss that critical email again! 🎯
