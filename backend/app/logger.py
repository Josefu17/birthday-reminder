import logging
import sys
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("BirthdayApp")
logger.setLevel(logging.INFO)

# Console Handler (prints to terminal)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_format)

# File Handler (saves to file, rotates when it gets too big)
# Max size: 5MB, Keep last 3 files
file_handler = RotatingFileHandler("birthday_bot.log", maxBytes=5*1024*1024, backupCount=3)
file_handler.setLevel(logging.INFO)
file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)