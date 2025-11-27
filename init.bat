@echo off
REM TelecomTools Suite - Database Initialization Script

echo ============================================
echo  TelecomTools Suite - Initialize Database
echo ============================================
echo.

REM Set environment variable for SQLite
set DATABASE_URL=sqlite:///./telecom.db

REM Activate virtual environment if exists
if exist "venv\" (
    call venv\Scripts\activate.bat
)

REM Initialize database
python scripts\init_db.py

echo.
echo ============================================
echo  Credentials:
echo  Email: admin@telecom.com
echo  Password: admin123
echo ============================================
echo.
pause

