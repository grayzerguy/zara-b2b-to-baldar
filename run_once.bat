@echo off
REM ==========================================================
REM  הרצה בודדת של הבוט — לשימוש עם Task Scheduler (שעתי).
REM  Action:     Program/script = run_once.bat
REM  Start in    = תיקיית הפרויקט (או השאר ריק, הסקריפט מטפל)
REM
REM  לבדיקה ידנית: פתח חלון PowerShell/CMD בתיקייה והרץ run_once.bat
REM ==========================================================

REM מעבר לתיקיית הסקריפט (נייד — בלי נתיב קשיח)
cd /d "%~dp0"

python main.py --once

REM קוד יציאה חוזר ל-Task Scheduler (0 = הצליח)
exit /b %ERRORLEVEL%
