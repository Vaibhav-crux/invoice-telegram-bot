import logging
import re
import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from app.core.config import settings
from app.services.telegram import save_uploaded_pdf
from app.core.db_config import get_db
from app.models.invoice_pdf import InvoicePDF
from app.models.invoice_json import InvoiceJSON
from app.services.gemini_service import process_text_with_gemini
from app.utils.file_utils import delete_file
from app.utils.keyboard_utils import get_invoice_keyboard
from datetime import datetime
import pdfplumber
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Conversation states
SELECT_INVOICE, AWAITING_PDF = range(2)

async def invoices_handler(update: Update, context):
    """Handle /invoices command or 'invoices' text message."""
    reply_markup = get_invoice_keyboard()
    await update.message.reply_text(
        text="Please select an invoice type:",
        reply_markup=reply_markup
    )
    logger.info("Sent invoice options keyboard to chat_id: %s", update.message.chat_id)
    return SELECT_INVOICE

async def callback_query_handler(update: Update, context):
    """Handle inline keyboard button clicks."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback
    invoice_type = query.data
    context.user_data['invoice_type'] = invoice_type  # Store selected invoice type
    await query.message.reply_text(
        f"You selected: {invoice_type.replace('_', ' ').title()}. Please upload a PDF file."
    )
    logger.info("User selected invoice type: %s", invoice_type)
    return AWAITING_PDF

async def handle_pdf_upload(update: Update, context):
    """Handle PDF file upload."""
    if not update.message.document or update.message.document.mime_type != "application/pdf":
        await update.message.reply_text("Please upload a valid PDF file.")
        return AWAITING_PDF

    invoice_type = context.user_data.get('invoice_type')
    if not invoice_type:
        await update.message.reply_text("No invoice type selected. Please start again with /invoices or 'invoices'.")
        return ConversationHandler.END

    file = await update.message.document.get_file()
    file_name = update.message.document.file_name or "invoice"
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    formatted_file_name = f"{file_name}_{invoice_type}_{current_time}.pdf"

    # Download the PDF file
    pdf_path = os.path.join("files", "temp_pdf", formatted_file_name)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    await file.download_to_drive(pdf_path)

    try:
        # Save the PDF
        save_uploaded_pdf(pdf_path)
        logger.info("PDF saved to %s", pdf_path)
        await update.message.reply_text("Processing...")

        # Extract text from PDF
        extracted_text = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text.append(text)
            extracted_text = "\n".join(extracted_text)  # Combine text from all pages
            logger.info("PDF text extracted for %s", pdf_path)
        except Exception as e:
            logger.error("Failed to extract PDF text: %s", str(e))
            await update.message.reply_text(f"Failed to extract PDF text: {str(e)}")
            return ConversationHandler.END

        # Save to invoice_pdfs table
        db = next(get_db())
        try:
            invoice_pdf = InvoicePDF(
                filename=formatted_file_name,
                invoice_type=invoice_type,
                extracted_text=extracted_text
            )
            db.add(invoice_pdf)
            db.commit()
            logger.info("Saved invoice data to database for %s", formatted_file_name)
        except Exception as e:
            db.rollback()
            logger.error("Failed to save to invoice_pdfs: %s", str(e))
            await update.message.reply_text(f"Failed to save invoice data: {str(e)}")
            return ConversationHandler.END

        # Delete the original PDF
        try:
            await delete_file(pdf_path)
        except Exception as e:
            await update.message.reply_text(f"Failed to delete PDF: {str(e)}")
            return ConversationHandler.END

        # Send extracted text to Gemini API
        try:
            gemini_json = await process_text_with_gemini(extracted_text, invoice_type, formatted_file_name)
        except Exception as e:
            await update.message.reply_text(f"Failed to process text with Gemini: {str(e)}")
            return ConversationHandler.END

        # Save Gemini JSON response to invoice_jsons table
        try:
            invoice_json = InvoiceJSON(
                invoice_type=invoice_type,
                json_data=json.dumps(gemini_json, indent=2, ensure_ascii=False)
            )
            db.add(invoice_json)
            db.commit()
            logger.info("Saved Gemini JSON to database for invoice_type: %s", invoice_type)
        except Exception as e:
            db.rollback()
            logger.error("Failed to save to invoice_jsons: %s", str(e))
            await update.message.reply_text(f"Failed to save Gemini JSON: {str(e)}")
            return ConversationHandler.END
        finally:
            db.close()

        # Send success message to Telegram
        invoice_type_display = invoice_type.replace('_', ' ').title()
        await update.message.reply_text(f"Record Saved into {invoice_type_display} table")

    except Exception as e:
        await update.message.reply_text(f"Failed to process PDF: {str(e)}")
        logger.error("Failed to process PDF: %s", str(e))
        return ConversationHandler.END

    return ConversationHandler.END

async def cancel(update: Update, context):
    """Cancel the conversation."""
    await update.message.reply_text("Operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

def setup_telegram_handlers(application: Application):
    """Set up Telegram bot handlers."""
    # Conversation handler for invoice selection and PDF upload
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("invoices", invoices_handler),
            MessageHandler(filters.TEXT & filters.Regex(re.compile(r'^invoices$', re.IGNORECASE)), invoices_handler),
        ],
        states={
            SELECT_INVOICE: [CallbackQueryHandler(callback_query_handler)],
            AWAITING_PDF: [MessageHandler(filters.Document.PDF, handle_pdf_upload)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False  # Disable per-message tracking for CallbackQueryHandler
    )
    application.add_handler(conv_handler)
    logger.info("Telegram handlers set up successfully")