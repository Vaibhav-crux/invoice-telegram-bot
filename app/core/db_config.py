from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from app.models.base_model import Base
from app.models.invoice_pdf import InvoicePDF
from app.models.invoice_json import InvoiceJSON
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# SQLite database file in project root
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "invoices.db")
DB_URL = f"sqlite:///{DB_PATH}"

# Create engine
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

# Create tables
def init_db():
    logger.info("Checking and creating tables for SQLite database: %s", DB_PATH)
    Base.metadata.create_all(engine)
    logger.info("Database tables initialized: %s", DB_PATH)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()