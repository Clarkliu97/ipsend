import os
import time
import json
import logging
import requests

from logging.handlers import TimedRotatingFileHandler

# ----------------- Logging Setup ------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Common log format (adjust as you see fit)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# 1) Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 2) Timed rotating file handler
#
#    - 'when="midnight"' means rotate at 00:00 local time
#    - 'interval=1' rotates every 1 day
#    - 'backupCount=7' keeps 7 old log files (adjust as desired)
#    - 'suffix' sets how the rotated files are named
file_handler = TimedRotatingFileHandler(
    "ipsend.log", 
    when="midnight", 
    interval=1, 
    backupCount=7
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
file_handler.suffix = "%Y-%m-%d-%H-%M-%S"  # e.g. ipsend.log.2025-03-19-00-00-00
logger.addHandler(file_handler)

# ----------------- Script Configuration ------------------

IP_CACHE_FILE = "ip_cache.txt"
CONFIG_FILE = "cred.json"

def load_config(config_file=CONFIG_FILE):
    """
    Load the MailerSend config (API key, from_email, to_email) from a JSON file.
    The JSON should look like:
    {
        "MAILERSEND_API_KEY": "your-api",
        "FROM_EMAIL": "your-from-email",
        "TO_EMAIL": "your-to-email"
    }
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)

def get_public_ip():
    """
    Retrieve the public IP address from ipify.org (JSON format).
    Returns the IP string, or None if there's an error.
    """
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["ip"]
    except (requests.RequestException, ValueError) as e:
        logger.error(f"Error retrieving IP: {e}")
        return None

def read_last_ip(cache_file=IP_CACHE_FILE):
    """
    Reads the last known IP from a cache file, or returns None if it doesn't exist.
    """
    if not os.path.exists(cache_file):
        return None
    with open(cache_file, "r", encoding="utf-8") as f:
        return f.read().strip()

def write_last_ip(ip, cache_file=IP_CACHE_FILE):
    """
    Writes the latest IP to the cache file.
    """
    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(ip)

def send_email_mailersend(api_key, from_email, to_email, subject, body):
    """
    Send an email using MailerSend's API.
    Reference: https://www.mailersend.com/help/api/v1/email
    """
    try:
        url = "https://api.mailersend.com/v1/email"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "from": {"email": from_email},
            "to": [{"email": to_email}],
            "subject": subject,
            "text": body,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"Email sent successfully to {to_email}")
    except requests.RequestException as e:
        logger.error(f"Failed to send email via MailerSend: {e}")

def main():
    # Load configuration from cred.json
    config = load_config(CONFIG_FILE)
    mailersend_api_key = config["MAILERSEND_API_KEY"] if "MAILERSEND_API_KEY" in config else os.getenv("MAILERSEND_API_KEY") if os.getenv("MAILERSEND_API_KEY") else None
    if mailersend_api_key is None:
        raise ValueError("MAILERSEND_API_KEY not found in config file or environment variables.")
    from_email = config["FROM_EMAIL"]
    to_email = config["TO_EMAIL"]

    # Read the cached IP (if exists)
    last_ip = read_last_ip()

    # Loop indefinitely
    while True:
        current_ip = get_public_ip()
        if current_ip is None:
            logger.error("Could not retrieve IP. Skipping email...")
        else:
            if current_ip != last_ip:
                # IP changed → send email, update cache
                logger.info(f"Public IP Now: {current_ip}")
                subject = "Current Public IP Address"
                body = f"{current_ip}"
                send_email_mailersend(
                    mailersend_api_key,
                    from_email,
                    to_email,
                    subject,
                    body
                )
                write_last_ip(current_ip)
                last_ip = current_ip
            else:
                logger.info("Public IP has not changed. No email sent.")

        # Sleep 30 minutes before repeating
        time.sleep(1800)

if __name__ == "__main__":
    main()
