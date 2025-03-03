#!/bin/bash

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing dependencies..."
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx

echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Starting Flask app..."
python app.py &

echo "Configuring Nginx..."
sudo bash -c 'cat > /etc/nginx/sites-available/flask_app <<EOF
server {
    listen 80;
    server_name your_domain_or_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF'

sudo ln -s /etc/nginx/sites-available/flask_app /etc/nginx/sites-enabled
sudo nginx -t && sudo systemctl restart nginx

echo "Setting up SSL with Let's Encrypt..."
sudo certbot --nginx -d your_domain_or_IP --non-interactive --agree-tos -m shraga771@gmail.com
sudo systemctl restart nginx

echo "Deployment complete! Your app should be running with SSL enabled."
