@echo off
TITLE Sproug Hub Foundation - NGO Portal Launcher

echo ========================================================
echo  Starting Sproug Hub Foundation NGO Portal Setup...    
echo ========================================================

cd /d "%~dp0"

WHERE python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Error: Python interpreter is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org and try again.
    pause
    exit /b 1
)

echo Python interpreter detected.

IF NOT EXIST "venv" (
    echo Creating virtual environment in 'venv'...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies from requirements.txt...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt

echo Validating database integrity...
python -c "import sqlite3, os; db='db.sqlite3'; [os.remove(db) for _ in [1] if os.path.exists(db) and (lambda: (lambda c: not c or c[0]!='ok')(sqlite3.connect(db).execute('PRAGMA integrity_check;').fetchone()))()]" 2>nul

echo Applying database migrations...
python manage.py migrate --noinput

echo Ensuring initial database records...
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_project.settings'); django.setup(); from portal.seed import seed_database; seed_database()"

echo ========================================================
echo  NGO Portal setup complete!
echo  Starting local server at http://127.0.0.1:8000/
echo  Access Admin Login with Username: Maverick / Pass: Yashraj@7777
echo ========================================================

python manage.py runserver 0.0.0.0:8000

pause
