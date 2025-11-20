# Installation script for ClasseViva Monitor Bot
# Run this on your Raspberry Pi

#!/bin/bash

echo "ClasseViva Monitor Bot - Installation Script"
echo "=============================================="

# Update system
echo "Updating system packages..."
sudo apt update

# Install dependencies
echo "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv git libpoppler-cpp-dev poppler-utils

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate and install requirements
echo "Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment template
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your credentials"
fi

echo ""
echo "Installation completed!"
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run: source venv/bin/activate && python bot.py"
echo "3. Or install as systemd service (see README.md)"
