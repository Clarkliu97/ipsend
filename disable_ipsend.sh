#!/bin/bash

# Stop the service if running
sudo systemctl stop ipsend.service

# Disable it so it won't start on boot
sudo systemctl disable ipsend.service

# Remove the service file
sudo rm /etc/systemd/system/ipsend.service

# Reload systemd to forget the removed service
sudo systemctl daemon-reload

echo "ipsend.service has been disabled and removed."
