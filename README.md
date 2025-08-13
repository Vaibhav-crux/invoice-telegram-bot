# Invoice Telegram Bot

The **Invoice Telegram Bot** is a Python-based application that allows users to upload PDF invoices via Telegram, categorize them by invoice type (Proforma, Sales, Overdue, Retainer), extract text using `pdfplumber`, process the text with the Gemini API to generate structured JSON, and store the data in a SQLite database. The bot is built with FastAPI for backend APIs, SQLAlchemy for SQLite database operations, and `python-telegram-bot` for Telegram integration. A simple frontend is included for potential UI interactions.

This project is designed to streamline invoice processing for small businesses or developers needing automated PDF parsing and data storage.

## Features

- **Telegram Bot Interface**:
  - Users can start the process with the `/invoices` command or by typing "invoices".
  - Select invoice types (Proforma Invoice, Sales Invoice, Overdue Invoice, Retainer Invoice) via an inline keyboard.
  - Upload PDF invoices, which are processed and deleted after extraction.
- **PDF Processing**:
  - Extracts text from uploaded PDFs using `pdfplumber`.
  - Sends extracted text to the Gemini API to generate structured JSON data (e.g., invoice number, amount, items).
- **Database Storage**:
  - Stores PDF metadata and extracted text in the `invoice_pdfs` table.
  - Stores Gemini-generated JSON data in the `invoice_jsons` table.
- **Asynchronous Operations**:
  - Uses `aiofiles` for non-blocking file deletion.
  - Integrates with FastAPI for scalable API endpoints.
- **Modular Design**:
  - Separates concerns into services (`gemini_service`, `telegram_handler`), utilities (`file_utils`, `keyboard_utils`), and models (`invoice_pdf`, `invoice_json`).
- **Logging and Error Handling**:
  - Comprehensive logging for debugging and monitoring.
  - User-friendly error messages sent via Telegram.

## Project Structure

```
invoice_telegram/
├── .env                    # Environment variables (e.g., GEMINI_API_KEY, TELEGRAM_BOT_TOKEN)
├── .env.example            # Template for environment variables
├── .gitignore              # Git ignore file
├── README.md               # Project documentation (this file)
├── requirements.txt        # Python dependencies
├── app/                    # Main application code
│   ├── main.py             # FastAPI application entry point
│   ├── __init__.py         # Package initializer
│   ├── core/               # Core configuration and utilities
│   │   ├── auth.py         # Authentication logic
│   │   ├── config.py       # Configuration settings (e.g., environment variables)
│   │   ├── db_config.py    # Database configuration and initialization
│   │   ├── logging.py      # Logging configuration
│   │   └── __init__.py
│   ├── middleware/         # FastAPI middleware
│   │   ├── cors.py         # CORS middleware
│   │   ├── error.py        # Error handling middleware
│   │   ├── gzip.py         # GZIP compression middleware
│   │   ├── logging.py      # Request logging middleware
│   │   └── rate_limiter.py # Rate limiting middleware
│   ├── models/             # SQLAlchemy models
│   │   ├── base_model.py   # Base model for shared fields (id, timestamps)
│   │   ├── invoice_json.py # Model for storing Gemini JSON data
│   │   └── invoice_pdf.py  # Model for storing PDF metadata and text
│   ├── routes/             # FastAPI route definitions
│   │   ├── invoice.py      # Invoice-related API endpoints
│   │   └── pdf.py          # PDF-related API endpoints
│   ├── schemas/            # Pydantic schemas for API validation
│   │   ├── invoice.py      # Invoice-related schemas
│   │   └── pdf.py          # PDF-related schemas
│   ├── services/           # Business logic and services
│   │   ├── bot_commands.py # Telegram bot command registration
│   │   ├── gemini_service.py # Gemini API processing
│   │   ├── invoice.py      # Invoice service logic
│   │   ├── pdf_service.py  # PDF processing logic
│   │   ├── telegram.py     # Telegram PDF saving logic
│   │   └── telegram_handler.py # Telegram bot handlers
│   ├── utils/              # Utility functions
│   │   ├── file_utils.py   # File operations (e.g., async deletion)
│   │   ├── keyboard_utils.py # Telegram inline keyboard definitions
│   │   ├── pdf.py          # PDF utility functions
│   │   └── session_tracker.py # Session tracking utilities
├── frontend/               # Frontend assets
│   ├── index.html          # Main HTML file
│   ├── script.js           # JavaScript logic
│   └── styles.css          # CSS styles
```

## Installation

### Prerequisites
- Python 3.9+
- db (included with Python)
- Telegram account and bot token (obtained from [BotFather](https://t.me/BotFather))
- Gemini API key (from Google Cloud or relevant provider)

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Vaibhav-crux/invoice-telegram-bot.git
   cd invoice-telegram-bot
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` with your values:
     ```
     TELEGRAM_BOT_TOKEN=your_bot_token
     CHAT_ID=your_chat_id
     GEMINI_API_KEY=your_gemini_api_key
     PORT=8000
     HOST=0.0.0.0
     ```

5. **Initialize the Database**:
   - The SQLite database (`invoices.db`) is automatically created on startup if it doesn't exist.
   - Tables (`invoice_pdfs`, `invoice_jsons`) are initialized via `app/core/db_config.py`.

## Running the Project

1. **Start the FastAPI Server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   - The `--reload` flag enables auto-reload for development.
   - The server runs at `http://127.0.0.1:8000`.

2. **Verify Startup**:
   - Check logs for:
     - "Application startup complete"
     - "Checking and creating tables for database: {path}"
     - "Database tables initialized: {path}"
     - "Bot commands registered successfully: ['invoices', 'help', 'status']"
     - "Telegram handlers set up successfully"

3. **Interact with the Telegram Bot**:
   - Open Telegram and start a chat with your bot.
   - Use the `/invoices` command or type "invoices" to begin.

## Usage

1. **Start the Invoice Process**:
   - Send `/invoices` or type "invoices" in Telegram.
   - Select an invoice type from the inline keyboard (Proforma Invoice, Sales Invoice, Overdue Invoice, Retainer Invoice).

2. **Upload a PDF**:
   - After selecting an invoice type, upload a PDF file.
   - The bot replies with "Processing...".

3. **Processing Steps**:
   - The PDF is saved to `files/temp_pdf/`.
   - Text is extracted using `pdfplumber`.
   - Extracted text is stored in the `invoice_pdfs` table.
   - The PDF is deleted asynchronously.
   - The text is sent to the Gemini API to generate structured JSON.
   - The JSON is stored in the `invoice_jsons` table.
   - The bot sends a confirmation: `Record Saved into {Selected Option} table`.

4. **API Endpoints**:
   - Access FastAPI endpoints (defined in `app/routes/invoice.py` and `app/routes/pdf.py`) at `http://127.0.0.1:8000`.
   - Check `/docs` for Swagger UI documentation.

5. **Frontend**:
   - Open `frontend/index.html` in a browser for a basic UI (if configured to interact with the backend).


## Testing

1. **Run the Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Test Telegram Bot**:
   - Send `/invoices` or type "invoices".
   - Verify the inline keyboard displays four options in two rows.
   - Select an option (e.g., Sales Invoice) and upload a PDF.
   - Check for the "Processing..." message.
   - Verify the SQLite database entries in `invoice_pdfs` and `invoice_jsons`.
   - Confirm the PDF is deleted from `files/temp_pdf`.
   - Check for the Telegram message: `Record Saved into Sales Invoice table`.

3. **Test Error Scenarios**:
   - Upload a non-PDF file to verify error handling.
   - Use an invalid `GEMINI_API_KEY` to check Gemini API error handling.
   - Make `files/temp_pdf` read-only to test file deletion errors.

4. **Verify Logs**:
   - Check logs for successful operations and error messages (in console or configured log file).
   - Example log entries:
     - "PDF saved to {path}"
     - "PDF text extracted for {path}"
     - "Saved invoice data to SQLite database for {filename}"
     - "File deleted: {path}"
     - "Raw Gemini response for {filename}: {json}"
     - "Saved Gemini JSON to SQLite database for invoice_type: {type}"

5. **Test Frontend**:
   - Open `frontend/index.html` and verify connectivity to FastAPI endpoints (if implemented).
