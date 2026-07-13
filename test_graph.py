"""
סקריפט אבחון ל-Microsoft Graph — בודק אימות + גישה לתיבה, בלי לשלוח כלום לבלדר
ובלי לסמן קבצים כמעובדים.

הרצה:  python test_graph.py

בודק, שלב אחר שלב:
  1. שכל משתני הסביבה מוגדרים
  2. שמצליחים לקבל access token (אימות תקין)
  3. שמצליחים לקרוא את התיבה (הרשאת Mail.Read + מדיניות גישה)
  4. כמה מיילים מהשולח נמצאו, וכמה מהם עם קובץ xlsx
"""
import sys
import requests
from datetime import datetime, timedelta

from config import (
    SENDER_EMAIL,
    GRAPH_TENANT_ID, GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET, MAILBOX_ADDRESS,
)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def fail(msg):
    print(f"\n❌ {msg}")
    sys.exit(1)


def main():
    print("=" * 60)
    print("בדיקת חיבור Microsoft Graph (read-only, לא נשלח כלום לבלדר)")
    print("=" * 60)

    # --- שלב 1: משתני סביבה ---
    print("\n[1] בדיקת משתני סביבה:")
    checks = {
        'GRAPH_TENANT_ID': GRAPH_TENANT_ID,
        'GRAPH_CLIENT_ID': GRAPH_CLIENT_ID,
        'GRAPH_CLIENT_SECRET': GRAPH_CLIENT_SECRET,
        'MAILBOX_ADDRESS': MAILBOX_ADDRESS,
    }
    missing = [k for k, v in checks.items() if not v]
    for k, v in checks.items():
        if k == 'GRAPH_CLIENT_SECRET' and v:
            shown = v[:3] + "***" + f" (אורך {len(v)})"
        else:
            shown = v or "(חסר!)"
        print(f"    {k:22} = {shown}")
    if missing:
        fail(f"חסרים משתני סביבה: {missing}. הגדר אותם והרץ שוב.")
    print("    ✅ כל המשתנים מוגדרים")

    # --- שלב 2: קבלת token ---
    print("\n[2] קבלת access token...")
    token_url = f"https://login.microsoftonline.com/{GRAPH_TENANT_ID}/oauth2/v2.0/token"
    try:
        resp = requests.post(token_url, data={
            'client_id': GRAPH_CLIENT_ID,
            'client_secret': GRAPH_CLIENT_SECRET,
            'scope': 'https://graph.microsoft.com/.default',
            'grant_type': 'client_credentials',
        }, timeout=30)
    except Exception as e:
        fail(f"החיבור ל-Microsoft נכשל (רשת/פיירוול?): {e}")
    if resp.status_code != 200:
        fail(f"אימות נכשל (HTTP {resp.status_code}):\n    {resp.text}\n"
             "בדוק tenant/client id ואת סוד האפליקציה.")
    token = resp.json().get('access_token')
    if not token:
        fail(f"לא התקבל token: {resp.text}")
    print("    ✅ אימות תקין — התקבל access token")

    headers = {'Authorization': f'Bearer {token}'}

    # --- שלב 3: קריאת התיבה ---
    print(f"\n[3] קריאת התיבה '{MAILBOX_ADDRESS}'...")
    cutoff = (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
    url = f"{GRAPH_BASE}/users/{MAILBOX_ADDRESS}/messages"
    resp = requests.get(url, headers=headers, params={
        '$filter': f"receivedDateTime ge {cutoff}",
        '$orderby': 'receivedDateTime desc',
        '$top': '50',
    }, timeout=30)
    if resp.status_code == 403:
        fail(f"אין הרשאה לתיבה (HTTP 403):\n    {resp.text}\n"
             "ודא שהוענק admin consent ל-Mail.Read, ושמדיניות הגישה (אם הגדרת) כוללת את התיבה.")
    if resp.status_code == 404:
        fail(f"התיבה לא נמצאה (HTTP 404): '{MAILBOX_ADDRESS}'. בדוק את הכתובת.")
    if resp.status_code != 200:
        fail(f"קריאת התיבה נכשלה (HTTP {resp.status_code}):\n    {resp.text}")
    messages = resp.json().get('value', [])
    print(f"    ✅ גישה תקינה — {len(messages)} מיילים ב-7 הימים האחרונים")

    # --- שלב 4: סינון לפי שולח + קבצי xlsx ---
    print(f"\n[4] חיפוש מיילים מהשולח '{SENDER_EMAIL}' עם קובץ xlsx:")
    from_sender = 0
    xlsx_found = 0
    for msg in messages:
        sender = (msg.get('from', {}) or {}).get('emailAddress', {}).get('address', '') or ''
        if sender.lower() != SENDER_EMAIL.lower():
            continue
        from_sender += 1
        subject = msg.get('subject', '(ללא נושא)')
        received = msg.get('receivedDateTime', '?')
        marker = ""
        if msg.get('hasAttachments'):
            att = requests.get(
                f"{GRAPH_BASE}/users/{MAILBOX_ADDRESS}/messages/{msg['id']}/attachments",
                headers=headers, timeout=30,
            )
            if att.status_code == 200:
                names = [a.get('name', '') for a in att.json().get('value', [])]
                xlsx = [n for n in names if n.lower().endswith('.xlsx')]
                if xlsx:
                    xlsx_found += len(xlsx)
                    marker = f"  📎 xlsx: {xlsx}"
        print(f"    • {received}  |  {subject}{marker}")

    print(f"\n    סה\"כ מהשולח: {from_sender} מיילים, {xlsx_found} קבצי xlsx")

    print("\n" + "=" * 60)
    if xlsx_found:
        print("✅ הכל עובד! הבוט אמור למצוא ולהוריד את הדוחות.")
    else:
        print("⚠️  האימות והגישה תקינים, אבל לא נמצא xlsx מהשולח ב-7 הימים האחרונים.")
        print("    (ייתכן שפשוט אין דוח חדש כרגע — זה בסדר.)")
    print("=" * 60)


if __name__ == "__main__":
    main()
