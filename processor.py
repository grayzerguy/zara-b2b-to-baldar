import pandas as pd
import os
import requests
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from config import SENT_SHIPMENTS_LOG_FILE
from stores_data import stores_data
from payload_utils import generate_api_string, generate_xml_payload


def load_sent_shipments() -> set:
    """טוען את קבוצת מזהי המשלוחים שכבר נשלחו בהצלחה (מונע שליחה כפולה בריטריי)."""
    if not os.path.exists(SENT_SHIPMENTS_LOG_FILE):
        return set()
    with open(SENT_SHIPMENTS_LOG_FILE, 'r', encoding='utf-8') as f:
        return {line.strip() for line in f if line.strip()}


def record_sent_shipment(shipping_key: str):
    """מסמן מזהה משלוח כנשלח בהצלחה, כדי שלא יישלח שוב בהרצה הבאה."""
    with open(SENT_SHIPMENTS_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(shipping_key + '\n')


def process_report_file(filepath: str) -> bool:
    try:
        logging.info(f"Processing file: {filepath}")
        source_filename = filepath.split(os.sep)[-1]

        df1 = pd.read_excel(filepath)
        if 'Shipping bulk' not in df1.columns:
            logging.error("Missing column 'Shipping bulk'")
            return False

        df1.drop_duplicates(subset=['Shipping bulk'], keep='first', inplace=True)

        df2 = pd.DataFrame(stores_data)
        merged_df = pd.merge(df1, df2, left_on='Store', right_on='קוד ספרדי', how='left')

        if merged_df['קוד ספרדי'].isnull().any():
            logging.error("Unmatched store codes found")
            return False

        final_df = merged_df[['שם החנות', 'עיר', 'רחוב', 'מספר', 'Shipping bulk']].copy()

        endpoint_url = "https://crm.tapuzdelivery.co.il/baldarwebservice/Service.asmx"
        headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "http://tempuri.org/SaveData1"}

        sent_shipments = load_sent_shipments()
        success_count, failure_count, skipped_count, already_sent_count = 0, 0, 0, 0

        for _, row in final_df.iterrows():
            shipping_id = row['Shipping bulk']
            shipping_key = str(shipping_id).strip()

            # דילוג על משלוח שכבר נשלח בהצלחה בעבר -> מונע כפילויות בריטריי של אותו קובץ
            if shipping_key in sent_shipments:
                logging.info(f"Skipping already-sent shipment: {shipping_key}")
                already_sent_count += 1
                continue

            # בניית ה-payload פר-שורה: שורה פגומה מדולגת ולא מפילה את כל הקובץ
            try:
                api_string = generate_api_string(row, source_filename)
                xml_payload = generate_xml_payload(api_string)
            except Exception as e:
                logging.error(f"SKIPPED {shipping_id}: invalid row data: {e}")
                skipped_count += 1
                continue

            try:
                response = requests.post(endpoint_url, data=xml_payload.encode('utf-8'), headers=headers, timeout=30)
                response.raise_for_status()

                root = ET.fromstring(response.text)
                delivery_number = root.find('.//{http://tempuri.org/}DeliveryNumber')
                if delivery_number is not None:
                    record_sent_shipment(shipping_key)
                    sent_shipments.add(shipping_key)
                    logging.info(f"SUCCESS for {shipping_id}: {delivery_number.text}")
                    success_count += 1
                else:
                    logging.error(f"FAILURE for {shipping_id}: No delivery number in response")
                    failure_count += 1
            except Exception as e:
                logging.error(f"FAILURE for {shipping_id}: {e}")
                failure_count += 1

        logging.info(
            f"Summary: {success_count} success, {failure_count} fail, "
            f"{skipped_count} skipped, {already_sent_count} already-sent"
        )
        return failure_count == 0

    except Exception as e:
        logging.critical(f"Processing error: {e}", exc_info=True)
        return False
