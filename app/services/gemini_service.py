import logging
import json
import google.generativeai as genai
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

async def process_text_with_gemini(extracted_text: str, invoice_type: str, filename: str) -> dict:
    """
    Send extracted text to Gemini API and return the parsed JSON response with invoice_type included.
    
    Args:
        extracted_text (str): Text extracted from the PDF.
        invoice_type (str): Selected invoice type (e.g., proforma_invoice).
        filename (str): Formatted filename for logging purposes.
    
    Returns:
        dict: Parsed JSON response from Gemini with invoice_type added.
    
    Raises:
        Exception: If the Gemini API call or JSON parsing fails.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Convert the following invoice text into a JSON object with relevant key-value pairs (e.g., invoice_number, issued_date, amount, billed_to, items). Return only the raw JSON string, without markdown code blocks or any other text. Ensure the JSON is valid and includes meaningful fields based on the text.
        Text: {extracted_text}
        """
        response = model.generate_content(prompt)
        # Strip markdown code blocks or extra whitespace
        response_text = response.text.strip()
        if response_text.startswith('```json') and response_text.endswith('```'):
            response_text = response_text[7:-3].strip()
        logger.info("Raw Gemini response for %s: %s", filename, response_text)
        gemini_json = json.loads(response_text)  # Parse as JSON
        gemini_json['invoice_type'] = invoice_type  # Add invoice_type to JSON
        logger.info("Received JSON response from Gemini for %s", filename)
        return gemini_json
    except Exception as e:
        logger.error("Failed to process text with Gemini API for %s: %s", filename, str(e))
        raise