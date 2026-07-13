"""
קריאת מייל דרך Microsoft Graph API (app-only / client credentials).
מחליף את outlook_utils.py כשרצים על שרת בלי Outlook מותקן.

חושף את אותו ממשק כמו outlook_utils.py:
    - was_file_already_processed(filename)
    - mark_file_as_processed(filename)
    - download_excel_attachment_from_outlook(sender_email, save_folder)

דורש משתני סביבה: GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET, MAILBOX_ADDRESS
"""
import os
import base64
import logging
import requests
from datetime import datetime, timedelta
from config import (
    PROCESSED_LOG_FILE,
    GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET, MAILBOX_ADDRESS,
)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def was_file_already_processed(filename: str) -> bool:
    if not os.path.exists(PROCESSED_LOG_FILE):
        return False
    with open(PROCESSED_LOG_FILE, 'r', encoding='utf-8') as f:
        return filename in f.read().splitlines()


def mark_file_as_processed(filename: str):
    with open(PROCESSED_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(filename + '\n')


def _get_access_token() -> str:
    if not (GRAPH_TENANT_ID and GRAPH_CLIENT_ID and GRAPH_CLIENT_SECRET):
        raise RuntimeError(
            "חסרים משתני סביבה ל-Graph: GRAPH_TENANT_ID / GRAPH_CLIENT_ID / GRAPH_CLIENT_SECRET"
        )
    url = f"https://login.microsoftonline.com/{GRAPH_TENANT_ID}/oauth2/v2.0/token"
    data = {
        'client_id': GRAPH_CLIENT_ID,
        'client_secret': GRAPH_CLIENT_SECRET,
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials',
    }
    resp = requests.post(url, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()['access_token']


def download_excel_attachment_from_outlook(sender_email: str, save_folder: str) -> str:
    if not MAILBOX_ADDRESS:
        raise RuntimeError("חסר משתנה סביבה MAILBOX_ADDRESS (כתובת התיבה שמקבלת את הדוחות)")

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    token = _get_access_token()
    headers = {'Authorization': f'Bearer {token}'}

    # רק הודעות מהזמן האחרון (חלון של יממה, בטוח מבחינת אזורי זמן — Graph מחזיר UTC).
    # מניעת כפילויות מתבצעת ממילא דרך processed_files.log.
    cutoff = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    params = {
        '$filter': f"receivedDateTime ge {cutoff}",
        '$orderby': 'receivedDateTime desc',
        '$top': '25',
    }
    url = f"{GRAPH_BASE}/users/{MAILBOX_ADDRESS}/messages"
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    messages = resp.json().get('value', [])

    for msg in messages:
        if not msg.get('hasAttachments'):
            continue

        sender = (msg.get('from', {}) or {}).get('emailAddress', {}).get('address', '') or ''
        if sender.lower() != sender_email.lower():
            continue

        att_url = f"{GRAPH_BASE}/users/{MAILBOX_ADDRESS}/messages/{msg['id']}/attachments"
        att_resp = requests.get(att_url, headers=headers, timeout=30)
        att_resp.raise_for_status()

        for att in att_resp.json().get('value', []):
            name = att.get('name', '')
            if not name.lower().endswith('.xlsx'):
                continue

            if was_file_already_processed(name):
                logging.info(f"Skipping already processed file: {name}")
                continue

            content = att.get('contentBytes')
            if not content:
                logging.warning(f"Attachment '{name}' has no contentBytes, skipping")
                continue

            filepath = os.path.join(save_folder, name)
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(content))
            logging.info(f"Downloaded Excel file: {filepath}")
            return filepath

    return None
