from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from fpdf import FPDF
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
db = SQLAlchemy(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.Integer, unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(20), nullable=False)

@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.json
    new_customer = Customer(name=data['name'], email=data['email'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "Customer added successfully"})

@app.route('/invoices', methods=['POST'])
def create_invoice():
    data = request.json
    last_invoice = Invoice.query.order_by(Invoice.invoice_number.desc()).first()
    invoice_number = last_invoice.invoice_number + 1 if last_invoice else data.get('invoice_number', 1)
    
    new_invoice = Invoice(invoice_number=invoice_number, customer_id=data['customer_id'], amount=data['amount'], date=data['date'])
    db.session.add(new_invoice)
    db.session.commit()
    return jsonify({"message": "Invoice created successfully", "invoice_number": invoice_number})

@app.route('/invoice/<int:invoice_id>/pdf', methods=['GET'])
def generate_invoice_pdf(invoice_id):
    invoice = Invoice.query.get(invoice_id)
    customer = Customer.query.get(invoice.customer_id)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Invoice #{invoice.invoice_number}", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Customer: {customer.name}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Amount: ${invoice.amount}", ln=True, align='L')
    pdf_file = f"invoice_{invoice.invoice_number}.pdf"
    pdf.output(pdf_file)
    return send_file(pdf_file, as_attachment=True)

if __name__ == '__main__':
 with app.app_context():
    db.create_all()

    app.run(debug=True, host='0.0.0.0', port=5000)
