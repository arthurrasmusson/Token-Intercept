#!/bin/bash

# install.sh - Install script for Token-Intercept
# This script sets up the daemon_server.py as a systemd service.

set -e

# Variables
SERVICE_NAME="token_intercept"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
USER="$(whoami)"
WORKING_DIR="$(pwd)"
PYTHON_EXEC="$(which python3)"

# Install required Python packages
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Generate gRPC code from the .proto file
echo "Generating gRPC code from generation_service.proto..."
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. generation_service.proto

# Create systemd service file
echo "Creating systemd service file..."

sudo bash -c "cat > ${SERVICE_FILE}" <<EOL
[Unit]
Description=Token Intercept Daemon Service
After=network.target

[Service]
Type=simple
ExecStart=${PYTHON_EXEC} ${WORKING_DIR}/daemon_server.py
User=${USER}
WorkingDirectory=${WORKING_DIR}
Restart=on-failure
StandardOutput=append:${WORKING_DIR}/token_intercept.log
StandardError=append:${WORKING_DIR}/token_intercept_error.log

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd daemon
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable and start the service
echo "Enabling and starting the ${SERVICE_NAME} service..."
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl start ${SERVICE_NAME}

echo "Installation complete. The ${SERVICE_NAME} service is now running."
