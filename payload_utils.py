from datetime import datetime
from xml.sax.saxutils import escape
from config import (
    BALDAR_COMPANY_CODE, BALDAR_BRANCH_NAME, BALDAR_BRANCH_CODE,
    BALDAR_CITY_ORIGIN, BALDAR_CLIENT_NAME, BALDAR_SERVICE_CODE
)

REQUIRED_FIELDS = ['רחוב', 'מספר', 'עיר', 'שם החנות', 'Shipping bulk']

def generate_api_string(row, source_filename):
    missing = [f for f in REQUIRED_FIELDS if f not in row or str(row[f]).strip() == '']
    if missing:
        raise ValueError(f"שדות חסרים בשורה: {missing}")

    now = datetime.now()
    today_date = now.strftime('%Y-%m-%d')
    run_timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    contact_person_info = f"{source_filename} at {run_timestamp}"

    params = [
        BALDAR_COMPANY_CODE,        # [0]  קוד חברה
        BALDAR_BRANCH_NAME,         # [1]  שם סניף
        BALDAR_BRANCH_CODE,         # [2]  קוד סניף
        BALDAR_CITY_ORIGIN,         # [3]  עיר מוצא
        str(row['רחוב']),           # [4]  רחוב יעד
        str(row['מספר']),           # [5]  מספר בית יעד
        str(row['עיר']),            # [6]  עיר יעד
        BALDAR_CLIENT_NAME,         # [7]  שם לקוח
        str(row['שם החנות']),       # [8]  שם נמען
        '',                         # [9]  טלפון נמען
        '1',                        # [10] סוג משלוח
        '0',                        # [11]
        '1',                        # [12]
        '1',                        # [13]
        '1',                        # [14]
        '0',                        # [15]
        str(row['Shipping bulk']),   # [16] מספר משלוח
        BALDAR_SERVICE_CODE,        # [17] קוד שירות
        str(row['Shipping bulk']),   # [18] מספר חבילה
        '',                         # [19]
        '',                         # [20]
        '',                         # [21]
        '',                         # [22]
        contact_person_info,        # [23] איש קשר / מקור
        '',                         # [24]
        '0',                        # [25]
        today_date,                 # [26] תאריך
        '',                         # [27]
        '',                         # [28]
        '',                         # [29]
        '',                         # [30]
        '',                         # [31]
        '',                         # [32]
        '',                         # [33]
        '',                         # [34]
        '',                         # [35]
        '',                         # [36]
        '',                         # [37]
        '',                         # [38]
        '',                         # [39]
    ]
    return ";".join(params)


def generate_xml_payload(api_string: str) -> str:
    escaped_param = escape(api_string)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <SaveData1 xmlns="http://tempuri.org/">
      <pParam>{escaped_param}</pParam>
    </SaveData1>
  </soap:Body>
</soap:Envelope>"""
