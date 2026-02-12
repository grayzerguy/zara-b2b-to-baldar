from datetime import datetime
from xml.sax.saxutils import escape

def generate_api_string(row, source_filename):
    now = datetime.now()
    today_date = now.strftime('%Y-%m-%d')
    run_timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    contact_person_info = f"{source_filename} at {run_timestamp}"

    params = [
        '1',
        'סלע',
        '1',
        'בית שמש ',
        str(row['רחוב']), 
        str(row['מספר']),
        str(row['עיר']),
        'ZARA B2B',
        str(row['שם החנות']), '',
        '1',
        '0',
        '1', 
        '1', 
        '1', 
        '0',
        str(row['Shipping bulk']),
        '4654',
         str(row['Shipping bulk']),
        '',
        '',
        '',
        '',
        contact_person_info,
        '',
        '0',
        today_date,
        '', 
        '', 
        '', 
        '', 
        '', 
        '', 
        '', 
        '',
        '', 
        '', 
        '', 
        '', 
        ''
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
