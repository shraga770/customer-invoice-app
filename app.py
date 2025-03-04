#!/bin/bash

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing dependencies..."
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx

echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install required fonts for Hebrew support
sudo apt install -y fonts-freefont-ttf

# Python script to generate Hebrew invoices
cat > app.py <<EOF
from fpdf import FPDF

class InvoicePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(200, 10, "חשבונית מס", ln=True, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, "תודה על הקנייה!", align="C")

    def add_invoice_details(self, invoice_data):
        self.set_font("Arial", "", 12)
        self.cell(0, 10, f'תאריך: {invoice_data["date"]}', ln=True, align="R")
        self.cell(0, 10, f'לקוח: {invoice_data["customer"]}', ln=True, align="R")
        self.cell(0, 10, f'סה"כ לתשלום: {invoice_data["total"]} ₪', ln=True, align="R")


def generate_invoice(invoice_data):
    pdf = InvoicePDF()
    pdf.add_page()
    pdf.add_invoice_details(invoice_data)
    pdf.output("invoice.pdf")

invoice_data = {
    "date": "04/03/2025",
    "customer": "ישראל ישראלי",
    "total": "500"
}

generate_invoice(invoice_data)
EOF

echo "Starting Flask app..."
python app.py &

echo "Configuring Nginx..."
sudo bash -c 'cat > /etc/nginx/sites-available/flask_app <<EOF
server {
    listen 80;
    server_name your_domain_or_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF'

sudo ln -s /etc/nginx/sites-available/flask_app /etc/nginx/sites-enabled
sudo nginx -t && sudo systemctl restart nginx

echo "Setting up SSL with Let's Encrypt..."
sudo certbot --nginx -d your_domain_or_IP --non-interactive --agree-tos -m SHRAGA771@GMAIL.COM
sudo systemctl restart nginx

echo "Deployment complete! Your app should be running with SSL enabled."
