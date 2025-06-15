"""Configuration settings for the bot and business information."""

import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env file")

# Business bot settings (existing)
BUSINESS_CONTACT_EMAIL = os.getenv("BUSINESS_CONTACT_EMAIL", "contact@example.com")
BUSINESS_HOURS = os.getenv("BUSINESS_HOURS", "9:00-18:00 Mon-Fri")
BUSINESS_DESCRIPTION = os.getenv("BUSINESS_DESCRIPTION", "Your business description here")
BUSINESS_SHORT_DESCRIPTION = os.getenv("BUSINESS_SHORT_DESCRIPTION")  # Optional
BUSINESS_INTRO_TITLE = os.getenv("BUSINESS_INTRO_TITLE")  # Optional
BUSINESS_INTRO_MESSAGE = os.getenv("BUSINESS_INTRO_MESSAGE")  # Optional
BUSINESS_INTRO_STICKER_FILE_ID = os.getenv("BUSINESS_INTRO_STICKER_FILE_ID")  # Optional
BUSINESS_LOCATION_LATITUDE = os.getenv("BUSINESS_LOCATION_LATITUDE")  # Optional
BUSINESS_LOCATION_LONGITUDE = os.getenv("BUSINESS_LOCATION_LONGITUDE")  # Optional
BUSINESS_LOCATION_ADDRESS = os.getenv("BUSINESS_LOCATION_ADDRESS")  # Optional
BUSINESS_OPENING_HOURS_TIME_ZONE = os.getenv("BUSINESS_OPENING_HOURS_TIME_ZONE")  # Optional
# For BUSINESS_OPENING_HOURS_INTERVALS, you might need to parse a JSON string from env
# e.g., import json; BUSINESS_OPENING_HOURS_INTERVALS = json.loads(os.getenv("BUSINESS_OPENING_HOURS_INTERVALS", "[]"))


# Hardcoded Business Connection Details (loaded from environment)
# These are used as a fallback if persistent storage isn't implemented yet
# or for a single, dedicated business account scenario.
HC_BUSINESS_CONNECTION_ID = os.getenv("HC_BUSINESS_CONNECTION_ID")
HC_BUSINESS_OWNER_CHAT_ID_STR = os.getenv("HC_BUSINESS_OWNER_CHAT_ID")

HC_BUSINESS_OWNER_CHAT_ID = None
if HC_BUSINESS_OWNER_CHAT_ID_STR:
    try:
        HC_BUSINESS_OWNER_CHAT_ID = int(HC_BUSINESS_OWNER_CHAT_ID_STR)
    except ValueError:
        print(f"Warning: HC_BUSINESS_OWNER_CHAT_ID ('{HC_BUSINESS_OWNER_CHAT_ID_STR}') is not a valid integer. Will be None.")

# You could also add a check here to ensure these are set if your logic strictly depends on them
# if not HC_BUSINESS_CONNECTION_ID or not HC_BUSINESS_OWNER_CHAT_ID:
#     print("Warning: HC_BUSINESS_CONNECTION_ID or HC_BUSINESS_OWNER_CHAT_ID is not set in .env. "
#           "Hardcoded fallback for business connection might not work.")


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = os.getenv("ADMIN_ID")
    DATABASE_URL = os.getenv("DATABASE_URL")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    # Add other configuration variables as needed


config = Config()
