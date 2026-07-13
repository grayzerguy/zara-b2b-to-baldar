import os
import sys
import time
import logging
from config import SENDER_EMAIL, SAVE_FOLDER, LOG_FILE
from graph_utils import download_excel_attachment_from_outlook, mark_file_as_processed
from processor import process_report_file

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("=== Starting automation cycle ===")
    filepath = download_excel_attachment_from_outlook(SENDER_EMAIL, SAVE_FOLDER)
    if filepath:
        if process_report_file(filepath):
            mark_file_as_processed(os.path.basename(filepath))
            logging.info(f"Processed successfully: {filepath}")
    else:
        logging.info("No new files found")
    logging.info("=== Cycle finished ===")

if __name__ == "__main__":
    # מצב הרצה בודדת: להרצה מתוזמנת (Task Scheduler / cron) פעם בשעה.
    # שימוש: python main.py --once   (או קביעת RUN_ONCE=1 בסביבה)
    run_once = '--once' in sys.argv or os.environ.get('RUN_ONCE') == '1'

    if run_once:
        try:
            main()
        except Exception as e:
            logging.critical(f"Fatal error in main loop: {e}", exc_info=True)
    else:
        while True:
            try:
                main()
            except Exception as e:
                logging.critical(f"Fatal error in main loop: {e}", exc_info=True)
            logging.info("Sleeping for 5 minutes.")
            time.sleep(300)
