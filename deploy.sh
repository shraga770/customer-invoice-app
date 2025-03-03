#!/bin/bash

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing dependencies..."
sudo apt install -y python3-pip python3-venv

echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Running Flask app..."
python app.py
