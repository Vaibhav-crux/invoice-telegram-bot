from xhtml2pdf import pisa
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_pdf(html_content: str, output_path: str, return_bytes: bool = False):
    try:
        # Ensure UTF-8 encoding
        html_content = html_content.encode('utf-8').decode('utf-8')
        # Convert HTML to PDF
        output = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=output, encoding='UTF-8')
        if pisa_status.err:
            logger.error("PDF generation failed with error code: %s", pisa_status.err)
            raise Exception("PDF generation failed")
        
        # Save to file
        with open(output_path, 'wb') as pdf_file:
            pdf_file.write(output.getvalue())
        
        logger.info("PDF generated successfully at: %s", output_path)
        
        # Return byte stream if requested
        if return_bytes:
            return output.getvalue()
    except Exception as e:
        logger.error("Error during PDF generation: %s", str(e))
        raise