import os

# כתובת השולח
SENDER_EMAIL = "dchartuv@mutagim.com"

# נתיבים
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FOLDER = os.path.join(BASE_DIR, "downloads")
LOG_FILE = os.path.join(BASE_DIR, "automation.log")
PROCESSED_LOG_FILE = os.path.join(BASE_DIR, "processed_files.log")
SENT_SHIPMENTS_LOG_FILE = os.path.join(BASE_DIR, "sent_shipments.log")

# קבועים ל-API של בלדר
BALDAR_COMPANY_CODE = '1'
BALDAR_BRANCH_NAME = 'סלע'
BALDAR_BRANCH_CODE = '1'
BALDAR_CITY_ORIGIN = 'בית שמש'
BALDAR_CLIENT_NAME = 'ZARA B2B'
BALDAR_SERVICE_CODE = '4654'
