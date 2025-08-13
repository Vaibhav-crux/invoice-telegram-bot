from datetime import datetime
import random
import string
import os
from app.utils.pdf import generate_pdf
from app.core.config import settings

# In-memory table data
table_data = []

def generate_invoice_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

def get_invoice_details():
    current_date = datetime.now().strftime("%d %B %Y")
    invoice_number = generate_invoice_number()
    return {
        "date_issued": current_date,
        "invoice_number": invoice_number,
        "issued_to": {
            "name": "Raghavendra",
            "address": "Dhanban Jharkhand, 826001"
        },
        "bank_details": {
            "bank_name": "Rimberio",
            "account_no": "012345678901"
        },
        "table_data": table_data
    }

def add_table_row(row):
    table_data.append({
        "no": len(table_data) + 1,
        "description": row.description,
        "quantity": row.quantity,
        "price": row.price,
        "subtotal": row.quantity * row.price
    })
    return {"message": "Row added successfully", "table_data": table_data}

def generate_and_save_pdf(html_content):
    filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) + '.pdf'
    filepath = os.path.join('files', filename)
    generate_pdf(html_content, filepath)
    return filename, filepath