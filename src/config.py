import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env file")

# Business bot settings
BUSINESS_CONTACT_EMAIL = os.getenv("BUSINESS_CONTACT_EMAIL", "contact@example.com")
BUSINESS_HOURS = os.getenv("BUSINESS_HOURS", "9:00-18:00 Mon-Fri")
BUSINESS_DESCRIPTION = os.getenv("BUSINESS_DESCRIPTION", "Your business description here")

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = os.getenv("ADMIN_ID")
    DATABASE_URL = os.getenv("DATABASE_URL")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    # Add other configuration variables as needed

config = Config()