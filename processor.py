import pandas as pd
import os
import requests
import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from stores_data import stores_data
from payload_utils import generate_api_string, generate_xml_payload

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
        final_df['api_string'] = final_df.apply(lambda row: generate_api_string(row, source_filename), axis=1)
        final_df['xml_payload'] = final_df['api_string'].apply(generate_xml_payload)

        endpoint_url = "https://crm.tapuzdelivery.co.il/baldarwebservice/Service.asmx"
        headers = {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "http://tempuri.org/SaveData1"}

        success_count, failure_count = 0, 0

        for _, row in final_df.iterrows():
            shipping_id = row['Shipping bulk']
            try:
                response = requests.post(endpoint_url, data=row['xml_payload'].encode('utf-8'), headers=headers, timeout=30)
                response.raise_for_status()

                root = ET.fromstring(response.text)
                delivery_number = root.find('.//{http://tempuri.org/}DeliveryNumber')
                if delivery_number is not None:
                    logging.info(f"SUCCESS for {shipping_id}: {delivery_number.text}")
                    success_count += 1
                else:
                    logging.error(f"FAILURE for {shipping_id}: No delivery number in response")
                    failure_count += 1
            except Exception as e:
                logging.error(f"FAILURE for {shipping_id}: {e}")
                failure_count += 1

        logging.info(f"Summary: {success_count} success, {failure_count} fail")
        return failure_count == 0

    except Exception as e:
        logging.critical(f"Processing error: {e}", exc_info=True)
        return False
