from sqlalchemy import Column, String, Text
from app.models.base_model import BaseModel, Base

class InvoiceJSON(BaseModel):
    __tablename__ = "invoice_jsons"
    
    invoice_type = Column(String, nullable=False)  # e.g., proforma_invoice, sales_invoice
    json_data = Column(Text, nullable=False)  # Gemini-generated JSON data as text