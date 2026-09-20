# Sproug Hub Foundation — Project Jhep NGO Teacher Portal

This is the official production-ready Content & Lesson Management Platform created and maintained by **Sproug Hub Foundation** for NGO teachers and administrators under **Project Jhep**.

---

## 🚀 One-Click Quick Start (Any Operating System)

Provided you have **Python 3.8+** installed on your system:

### 🪟 Windows Users:
1. Extract the downloaded ZIP file.
2. Double-click `run.bat` (or run `run.bat` in Command Prompt / PowerShell).
3. The script will automatically create a virtual environment, install dependencies, prepare the database, and launch the application at `http://127.0.0.1:8000/`.

### 🍎 macOS & 🐧 Linux Users:
1. Extract the downloaded ZIP file.
2. Open terminal in the extracted folder and run:
   ```bash
   ./run.sh
   ```
3. The launcher will set up `venv`, install requirements, migrate the database, and start the application at `http://127.0.0.1:8000/`.

---

## 🔑 Administrator Credentials

- **Username:** `Maverick`
- **Password:** `Yashraj@7777`
- **Role:** Platform Administrator (`Yashraj Bhogade`)

---

## 📦 Manual Setup (Optional)

If you prefer to run setup commands manually:

1. Create & activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate        # On Linux/macOS
   # OR venv\Scripts\activate.bat  # On Windows
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations & seed database:
   ```bash
   python manage.py migrate
   python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_project.settings'); django.setup(); from portal.seed import seed_database; seed_database()"
   ```
4. Start the server:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
