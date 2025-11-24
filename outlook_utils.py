import os
import logging
import win32com.client
from datetime import datetime
from config import PROCESSED_LOG_FILE

def was_file_already_processed(filename: str) -> bool:
    if not os.path.exists(PROCESSED_LOG_FILE):
        return False
    with open(PROCESSED_LOG_FILE, 'r', encoding='utf-8') as f:
        return filename in f.read().splitlines()

def mark_file_as_processed(filename: str):
    with open(PROCESSED_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(filename + '\n')

def download_excel_attachment_from_outlook(sender_email: str, save_folder: str) -> str:
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)  # Inbox
    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # 🆕 סינון לפי תאריך: רק מיילים מהיום
    today = datetime.now().date()

    for message in messages:
        try:
            if message.Class != 43:  # Mail item only
                continue

            # רק הודעות מהיום
            if message.ReceivedTime.date() < today:
                break  # כל ההודעות הבאות ישנות יותר, אפשר לעצור

            if message.SenderEmailAddress.lower() == sender_email.lower():
                if message.Attachments.Count > 0:
                    for attachment in message.Attachments:
                        if attachment.FileName.lower().endswith(".xlsx"):
                            filename = attachment.FileName
                            filepath = os.path.join(save_folder, filename)

                            if was_file_already_processed(filename):
                                logging.info(f"Skipping already processed file: {filename}")
                                continue

                            attachment.SaveAsFile(filepath)
                            logging.info(f"Downloaded Excel file: {filepath}")
                            return filepath
        except Exception as e:
            logging.error(f"Error processing email: {e}")
            continue

    return None
