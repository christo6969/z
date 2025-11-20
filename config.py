"""
Configuration file for ClasseViva Monitor Bot
Optimized for Raspberry Pi
"""

# Telegram API Configuration
API_ID = 26534737
API_HASH = "b68693742cb2f9e6b3cb99d09bdce12f"

# Bot Settings
BOT_TOKEN = ""  # Set your bot token here or via environment variable

# ClasseViva API Configuration
CLASSEVIVA_API_URL = "https://web.spaggiari.eu/rest/v1"

# Class Detection Settings
CLASS_PATTERN = r'\b([1-5][A-Z]{2})\b'  # Pattern to match classes like 1AA, 2BC, 5XY

# Raspberry Pi Optimization Settings
MAX_WORKERS = 2  # Limit concurrent workers for memory efficiency
ENABLE_LOGGING = True
LOG_LEVEL = "INFO"
LOG_FILE = "classeviva_monitor.log"

# PDF Processing Settings
MAX_PDF_SIZE_MB = 5  # Maximum PDF size to process (in MB)
PDF_TIMEOUT = 30  # Timeout for PDF processing in seconds
