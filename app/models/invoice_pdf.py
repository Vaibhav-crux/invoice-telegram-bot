from sqlalchemy import Column, String, Text
from app.models.base_model import BaseModel, Base

class InvoicePDF(BaseModel):
    __tablename__ = "invoice_pdfs"
    
    filename = Column(String, nullable=False)
    invoice_type = Column(String, nullable=False)  # e.g., proforma_invoice, sales_invoice
    extracted_text = Column(Text, nullable=True)  # Parsed text from PDF