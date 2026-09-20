#!/usr/bin/env bash
set -e

echo "========================================================"
echo " Starting Sproug Hub Foundation NGO Portal Setup...    "
echo "========================================================"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

PYTHON_BIN=""
if command -v python3 &> /dev/null; then
    PYTHON_BIN="python3"
elif command -v python &> /dev/null; then
    PYTHON_BIN="python"
else
    echo "Error: Python interpreter is not installed or not in PATH."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

echo "Using Python binary: $($PYTHON_BIN --version)"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment in 'venv'..."
    $PYTHON_BIN -m venv venv
fi

source venv/bin/activate

echo "Installing dependencies from requirements.txt..."
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo "Validating database integrity..."
python -c "import sqlite3, os; db='db.sqlite3'; [os.remove(db) for _ in [1] if os.path.exists(db) and (lambda: (lambda c: not c or c[0]!='ok')(sqlite3.connect(db).execute('PRAGMA integrity_check;').fetchone()))()]" 2>/dev/null || true

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Ensuring initial database records..."
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_project.settings'); django.setup(); from portal.seed import seed_database; seed_database()"

echo "========================================================"
echo " NGO Portal setup complete!"
echo " Starting local server at http://127.0.0.1:8000/ "
echo " Access Admin Login with Username: Maverick / Pass: Yashraj@7777"
echo "========================================================"

python manage.py runserver 0.0.0.0:8000
