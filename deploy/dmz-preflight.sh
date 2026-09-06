#!/usr/bin/env bash
# בדיקת מוכנות שרת DMZ עבור שירות zara-b2b-to-baldar.
# הרץ על שרת היעד:  bash dmz-preflight.sh
# יוצא 0 אם הכל תקין, 1 אם יש כשל חוסם.

set -uo pipefail

RUNTIME_HOSTS=(login.microsoftonline.com graph.microsoft.com crm.tapuzdelivery.co.il)
BUILD_HOSTS=(pypi.org files.pythonhosted.org registry-1.docker.io auth.docker.io)
FAIL=0
WARN=0

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=1; }
warn() { printf '  \033[33m!\033[0m %s\n' "$1"; WARN=1; }
head_() { printf '\n\033[1m%s\033[0m\n' "$1"; }

head_ "1. DNS"
for h in "${RUNTIME_HOSTS[@]}"; do
  if getent hosts "$h" >/dev/null 2>&1; then ok "$h נפתר"; else bad "$h לא נפתר — בדוק DNS ב-DMZ"; fi
done

head_ "2. יציאה החוצה — יעדי ריצה (חובה)"
for h in "${RUNTIME_HOSTS[@]}"; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "https://$h" 2>/dev/null)
  if [ "$code" != "000" ]; then ok "$h:443 נגיש (HTTP $code)"; else bad "$h:443 חסום — בקש פתיחה בפיירוול"; fi
done

head_ "3. יציאה החוצה — יעדי התקנה (לא חובה בריצה שוטפת)"
for h in "${BUILD_HOSTS[@]}"; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "https://$h" 2>/dev/null)
  if [ "$code" != "000" ]; then ok "$h נגיש"; else warn "$h חסום — תצטרך לבנות image בחוץ ולהעביר ב-docker save/load"; fi
done

head_ "4. TLS Inspection (הכשל הנפוץ ביותר)"
issuer=$(echo | timeout 15 openssl s_client -connect login.microsoftonline.com:443 \
         -servername login.microsoftonline.com 2>/dev/null \
         | openssl x509 -noout -issuer 2>/dev/null)
if [ -z "$issuer" ]; then
  warn "לא הצלחתי לקרוא את התעודה — כנראה חסום, חזור אחרי פתיחת הפיירוול"
elif echo "$issuer" | grep -qiE "microsoft|digicert|entrust|globalsign|baltimore"; then
  ok "אין TLS inspection ($(echo "$issuer" | cut -c1-70))"
else
  warn "TLS INSPECTION מזוהה! המנפיק: $issuer"
  echo "     → חלץ את ה-CA הארגונית, שמור כ-corp-ca.crt, ובקונטיינר הגדר:"
  echo "       REQUESTS_CA_BUNDLE=/etc/ssl/certs/corp-ca.crt"
  echo "     → אל תשתמש ב-verify=False. זה חושף את סוד ה-Graph."
fi

head_ "5. סטיית שעון (שוברת את טוקן ה-OAuth)"
remote=$(curl -sI --max-time 15 https://login.microsoftonline.com 2>/dev/null \
         | grep -i '^date:' | sed 's/^[Dd]ate: //' | tr -d '\r')
if [ -z "$remote" ]; then
  warn "לא ניתן לקרוא שעון מרוחק (היעד חסום) — בדוק שוב אחרי פתיחת הפיירוול"
else
  skew=$(( $(date +%s) - $(date -d "$remote" +%s) )); skew=${skew#-}
  if   [ "$skew" -le 60  ]; then ok   "סטייה ${skew} שניות — תקין"
  elif [ "$skew" -le 300 ]; then warn "סטייה ${skew} שניות — גבולי, הפעל NTP"
  else bad "סטייה ${skew} שניות — ה-OAuth ייכשל (AADSTS700024). פתח NTP 123/UDP או הגדר שרת זמן פנימי"
  fi
fi

head_ "6. Proxy"
if [ -n "${HTTPS_PROXY:-${https_proxy:-}}" ]; then
  ok "proxy מוגדר: ${HTTPS_PROXY:-$https_proxy} — העבר אותו כמשתנה סביבה לקונטיינר, אין שינוי קוד"
else
  ok "אין proxy מפורש — יציאה ישירה"
fi

head_ "7. Docker"
if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then ok "docker פעיל ($(docker --version | cut -d, -f1))"
  else bad "docker מותקן אך לא רץ / אין הרשאה — הרץ: sudo usermod -aG docker \$USER"; fi
else
  bad "docker לא מותקן — התקן: curl -fsSL https://get.docker.com | sh"
fi

head_ "סיכום"
if [ "$FAIL" -eq 1 ]; then
  printf '\033[31mיש כשלים חוסמים. תקן אותם לפני העלייה.\033[0m\n'; exit 1
elif [ "$WARN" -eq 1 ]; then
  printf '\033[33mעובר עם אזהרות — קרא אותן, חלקן ישברו בזמן ריצה.\033[0m\n'; exit 0
else
  printf '\033[32mהשרת מוכן.\033[0m\n'; exit 0
fi
