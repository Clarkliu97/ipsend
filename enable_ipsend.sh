#!/bin/bash

# Copy ipsend.service to systemd directory
sudo cp ipsend.service /etc/systemd/system/ipsend.service

# Reload systemd to read the new service
sudo systemctl daemon-reload

# Enable the service so it starts on boot
sudo systemctl enable ipsend.service

# Start the service immediately
sudo systemctl start ipsend.service

echo "ipsend.service has been installed, enabled, and started."
