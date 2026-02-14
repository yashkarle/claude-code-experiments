# Background Deployment Guide

Since you need this running 24/7 and can't rely on your laptop (which goes to sleep), here are reliable solutions.

---

## Recommended Solutions

### Option 1: Free Cloud Deployment (Easiest & Best) ⭐

Deploy to a free cloud service that runs 24/7:

#### **Oracle Cloud Free Tier (Recommended)**

**Why Oracle Cloud:**
- Completely FREE forever (not a trial)
- Always-on VM
- More than enough resources for this script
- No credit card required initially

**Steps:**

1. **Create Oracle Cloud Account**
   - Go to https://www.oracle.com/cloud/free/
   - Sign up for free tier (always free, not a trial)
   - Create an account

2. **Create a VM Instance**
   - Go to Compute → Instances → Create Instance
   - Name: `gmail-monitor`
   - Image: Ubuntu 22.04
   - Shape: VM.Standard.E2.1.Micro (Always Free)
   - Create SSH key pair (download the private key)
   - Create instance

3. **Connect to Your VM**
   ```bash
   ssh -i /path/to/private-key ubuntu@<your-instance-ip>
   ```

4. **Set Up the Monitor**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Python and pip
   sudo apt install python3 python3-pip git -y

   # Clone your repository
   git clone https://github.com/yashkarle/claude-code-experiments.git
   cd claude-code-experiments

   # Install dependencies
   pip3 install -r requirements.txt

   # Set up configuration
   nano .env
   # Paste your configuration from your local .env file
   # Save with Ctrl+X, Y, Enter
   ```

5. **Upload Gmail Credentials**
   On your local machine:
   ```bash
   scp -i /path/to/private-key credentials.json ubuntu@<your-instance-ip>:~/claude-code-experiments/
   ```

6. **First-time Authentication**
   Since the server has no browser, we'll authenticate on your laptop and transfer the token:

   **On your laptop:**
   ```bash
   # Make sure you already ran gmail_monitor.py locally and have token.pickle
   # Upload it to the server:
   scp -i /path/to/private-key token.pickle ubuntu@<your-instance-ip>:~/claude-code-experiments/
   ```

7. **Run as a System Service**
   On the VM:
   ```bash
   # Create service file
   sudo nano /etc/systemd/system/gmail-monitor.service
   ```

   Paste this content:
   ```ini
   [Unit]
   Description=Gmail Email Monitor
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/claude-code-experiments
   ExecStart=/usr/bin/python3 /home/ubuntu/claude-code-experiments/gmail_monitor.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable gmail-monitor
   sudo systemctl start gmail-monitor
   ```

8. **Check Status**
   ```bash
   sudo systemctl status gmail-monitor
   sudo journalctl -u gmail-monitor -f  # View live logs
   ```

**Done!** Your monitor runs 24/7, even when your laptop is off.

---

#### **Alternative Free Options**

**Google Cloud Platform (GCP)**
- $300 free credit for 90 days
- After that, ~$5-10/month for smallest VM
- Setup similar to Oracle Cloud

**AWS Free Tier**
- 750 hours/month free for 12 months
- t2.micro instance
- After 12 months, ~$8-10/month

**Railway.app / Render.com**
- Good for simple scripts
- May have limitations on free tier

---

### Option 2: Raspberry Pi (One-time Cost)

If you have or can get a Raspberry Pi:

**Pros:**
- One-time cost (~$50-100)
- Runs at home 24/7
- Very low power consumption (~$2-5/year electricity)
- Full control

**Setup:**
1. Install Raspberry Pi OS
2. Clone repository
3. Set up as systemd service (same as Oracle Cloud step 7)
4. Runs forever in your home

---

### Option 3: Always-On Home Server

If you have an old laptop or desktop that can stay on:

**Steps:**
1. Keep it plugged in and powered on
2. Disable sleep/hibernate in power settings:

   **Linux:**
   ```bash
   sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
   ```

   **macOS:**
   ```bash
   sudo pmset -a disablesleep 1
   ```

   **Windows:**
   - Settings → Power & Sleep → Never sleep

3. Run the script using `screen` or `systemd` service:
   ```bash
   screen -S gmail-monitor
   python3 gmail_monitor.py
   # Press Ctrl+A then D to detach
   ```

---

### Option 4: Docker Container on Cloud

If you're familiar with Docker:

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "gmail_monitor.py"]
```

Deploy to:
- Railway.app (has free tier)
- Render.com (has free tier)
- Fly.io (has free tier)
- Your own server with Docker

---

## My Recommendation

**For your use case (important emails over next few days):**

1. **Short-term (next few days):** Use Option 3 - keep your laptop on and disable sleep
   ```bash
   # On your laptop (macOS example):
   caffeinate -s python3 gmail_monitor.py
   # This prevents sleep while the script runs
   ```

2. **Long-term (best solution):** Use Oracle Cloud free tier
   - Takes 30 minutes to set up
   - Runs forever for free
   - No worries about laptop sleep
   - Can leave laptop off completely

---

## Quick Start: Laptop with Sleep Disabled

If you need this running TODAY and don't want to set up cloud:

**macOS:**
```bash
# Keep laptop awake while script runs
caffeinate -s python3 gmail_monitor.py
```

**Linux:**
```bash
# Install caffeine
sudo apt install caffeine

# Or use systemd-inhibit
systemd-inhibit --what=sleep python3 gmail_monitor.py
```

**Windows (PowerShell as Admin):**
```powershell
# Disable sleep
powercfg -change -standby-timeout-ac 0
powercfg -change -standby-timeout-dc 0

# Then run normally:
python gmail_monitor.py
```

---

## Monitoring Your Monitor

Once deployed, you can check if it's running:

**On cloud server:**
```bash
sudo systemctl status gmail-monitor
sudo journalctl -u gmail-monitor --since "10 minutes ago"
```

**With screen/tmux:**
```bash
screen -r gmail-monitor  # Reattach to see live output
```

**Check from anywhere:**
Add email yourself from one of the monitored addresses to test!

---

## Stopping/Updating

**Stop service:**
```bash
sudo systemctl stop gmail-monitor
```

**Update code:**
```bash
cd claude-code-experiments
git pull
sudo systemctl restart gmail-monitor
```

**View logs:**
```bash
sudo journalctl -u gmail-monitor -f
```

---

## Security Notes

When deploying to cloud:
1. Never commit `.env` file or credentials to git (already in `.gitignore`)
2. Use strong SSH keys, not passwords
3. Keep your cloud instance's firewall enabled
4. Only open SSH port (22), nothing else needed

---

Let me know which option you'd like to pursue and I can provide more detailed steps!
