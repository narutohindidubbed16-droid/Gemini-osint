import os

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Channel IDs (must be negative integer IDs, e.g., -1001234567890)
MAIN_CHANNEL = int(os.getenv("MAIN_CHANNEL", 0))
BACKUP_CHANNEL = int(os.getenv("BACKUP_CHANNEL", 0))
PRIVATE_CHANNEL = int(os.getenv("PRIVATE_CHANNEL", 0))

# API URLs (Ensure these are set in your environment)
MOBILE_API = os.getenv("MOBILE_API")
GST_API = os.getenv("GST_API")
IFSC_API = os.getenv("IFSC_API")
PINCODE_API = os.getenv("PINCODE_API")
VEHICLE_API = os.getenv("VEHICLE_API") # Base variable
RC_API = os.getenv("VEHICLE_API") # Alias used in handlers
IMEI_API = os.getenv("IMEI_API") # Added missing variable

# Admin Settings
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Default starting credits
START_CREDITS = int(os.getenv("START_CREDITS", "5"))

# Bot Info (For Webhook setup in main.py)
BOT_USERNAME = os.getenv("BOT_USERNAME", "NagiOSINTPROBot") 
