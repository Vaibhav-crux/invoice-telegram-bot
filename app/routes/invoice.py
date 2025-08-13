from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.schemas.invoice import TableRow, HtmlContent
from app.services.invoice import get_invoice_details, add_table_row, generate_and_save_pdf

router = APIRouter(prefix="/invoice", tags=["invoice"])

@router.get("/")
def get_invoice():
    return get_invoice_details()

@router.post("/add_row")
def add_row(row: TableRow):
    return add_table_row(row)

@router.post("/generate_pdf")
async def generate_pdf_endpoint(content: HtmlContent):
    filename, filepath = await generate_and_save_pdf(content.html)
    return FileResponse(filepath, media_type='application/pdf', filename=filename)