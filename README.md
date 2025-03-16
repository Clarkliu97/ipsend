# ipsend

Use [MailerSend](https://app.mailersend.com/dashboard) to send emails from your IP address. 

Put credentials in `cred.json` file.

```json
{
    "MAILERSEND_API_KEY": "your_api_key", 
    "FROM_EMAIL": "email_address_connected_to_api_key",
    "TO_EMAIL": "email_address_to_send_to"
}
```

Example ipsend.service file:

```ini
[Unit]
Description=Send IP (MailerSend) Python Script
After=network-online.target
Wants=network-online.target

[Service]
# Full path to Python and your script
ExecStart=your/path/to/python3 your/path/to/ipsend.py

# (Optional) run as a specific non-root user:
User=your_user
WorkingDirectory=your/path/to/ipsend

# Restart automatically if it stops
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

You can leave the ipsend.service file here and use the shell scripts provided to enable and disable the service.

