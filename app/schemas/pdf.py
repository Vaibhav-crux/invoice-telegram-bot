from pydantic import BaseModel

class PDFResponse(BaseModel):
    filename: str
    invoice_type: str
    extracted_text: str | None
    message: str