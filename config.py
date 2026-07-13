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

# Microsoft Graph — קריאת מייל בשרת (app-only). הסודות מוגדרים כמשתני סביבה, לא בקוד.
GRAPH_TENANT_ID = os.environ.get('GRAPH_TENANT_ID', '')
GRAPH_CLIENT_ID = os.environ.get('GRAPH_CLIENT_ID', '')
GRAPH_CLIENT_SECRET = os.environ.get('GRAPH_CLIENT_SECRET', '')
# כתובת התיבה שמקבלת את הדוחות (ה-UPN של תיבת היעד)
MAILBOX_ADDRESS = os.environ.get('MAILBOX_ADDRESS', '')
