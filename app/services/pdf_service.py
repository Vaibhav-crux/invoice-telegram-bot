import logging
import os
import fitz  # PyMuPDF
from sqlalchemy.orm import Session
from app.models.invoice_pdf import InvoicePDF
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def save_pdf_to_db(db: Session, filename: str, invoice_type: str, extracted_text: str | None):
    """Save PDF details to the database."""
    try:
        pdf_record = InvoicePDF(filename=filename, invoice_type=invoice_type, extracted_text=extracted_text)
        db.add(pdf_record)
        db.commit()
        db.refresh(pdf_record)
        logger.info("Saved PDF metadata to database: %s", filename)
        return pdf_record
    except Exception as e:
        logger.error("Failed to save PDF to database: %s", str(e))
        raise

def process_pdf(pdf_file: bytes, filename: str, invoice_type: str, db: Session):
    """Process uploaded PDF and save to database."""
    try:
        logger.info("Processing PDF: %s, type: %s", filename, invoice_type)
        # Validate input
        if not isinstance(pdf_file, (bytes, bytearray)):
            logger.error("Invalid PDF file type: %s", type(pdf_file))
            raise ValueError(f"Expected bytes or bytearray, got {type(pdf_file)}")
        
        # Create temporary directory
        temp_dir = os.path.join("files", "temp_pdf")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        temp_filename = f"{timestamp}_{filename}"
        temp_filepath = os.path.join(temp_dir, temp_filename)
        
        # Save PDF to temporary file
        with open(temp_filepath, "wb") as f:
            f.write(pdf_file)
            logger.info("Saved PDF to temporary file: %s", temp_filepath)
        
        # Save PDF to permanent files/ directory
        files_dir = "files"
        os.makedirs(files_dir, exist_ok=True)
        permanent_filepath = os.path.join(files_dir, filename)
        with open(permanent_filepath, "wb") as f:
            f.write(pdf_file)
            logger.info("Saved PDF to permanent file: %s", permanent_filepath)
        
        # Extract text from temporary PDF using PyMuPDF
        extracted_text = None
        logger.info("Opening PDF with PyMuPDF: %s", temp_filename)
        with fitz.open(temp_filepath) as pdf:
            logger.info("Extracting text from PDF: %s", temp_filename)
            text = ""
            for page in pdf:
                page_text = page.get_text("text")
                text += page_text or ""
            extracted_text = text if text else None
            logger.info("Extracted text length: %d characters", len(extracted_text or ""))
        
        # Save to database
        save_pdf_to_db(db, filename, invoice_type, extracted_text)
        logger.info("Processed PDF %s for invoice type %s", filename, invoice_type)
        
        # Delete temporary file
        try:
            os.remove(temp_filepath)
            logger.info("Deleted temporary PDF file: %s", temp_filepath)
        except Exception as e:
            logger.warning("Failed to delete temporary PDF file %s: %s", temp_filepath, str(e))
        
        return {
            "filename": filename,
            "invoice_type": invoice_type,
            "extracted_text": extracted_text,
            "message": "PDF processed and saved successfully"
        }
    except Exception as e:
        logger.error("Failed to process PDF %s: %s", filename, str(e))
        # Attempt to delete temporary file in case of failure
        if 'temp_filepath' in locals():
            try:
                os.remove(temp_filepath)
                logger.info("Deleted temporary PDF file on error: %s", temp_filepath)
            except Exception as e:
                logger.warning("Failed to delete temporary PDF file on error %s: %s", temp_filepath, str(e))
        raise