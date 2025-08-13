from fastapi import APIRouter, Depends, HTTPException, File
from sqlalchemy.orm import Session
from app.core.db_config import get_db
from app.services.pdf_service import process_pdf
from app.schemas.pdf import PDFResponse
import logging
import time

router = APIRouter(prefix="/pdf", tags=["pdf"])

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

@router.post("/process/{invoice_type}", response_model=PDFResponse)
async def process_pdf_endpoint(
    invoice_type: str,
    filename: str,
    file: bytes = File(...),
    db: Session = Depends(get_db)
):
    try:
        if not filename.endswith(".pdf"):
            logger.error("Invalid filename: %s", filename)
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        logger.info("Received PDF file for processing: %s, type: %s", filename, invoice_type)
        result = process_pdf(file, filename, invoice_type, db)
        logger.info("PDF processing completed: %s", filename)
        return result
    except Exception as e:
        logger.error("Error processing PDF: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")