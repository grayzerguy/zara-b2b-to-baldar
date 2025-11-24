import os

# כתובת השולח
SENDER_EMAIL = "dchartuv@mutagim.com"

# נתיבים
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FOLDER = os.path.join(BASE_DIR, "downloads")
LOG_FILE = os.path.join(BASE_DIR, "automation.log")
PROCESSED_LOG_FILE = os.path.join(BASE_DIR, "processed_files.log")
