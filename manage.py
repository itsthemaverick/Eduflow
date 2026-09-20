#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import sqlite3

def check_and_repair_sqlite_db():
    db_path = 'db.sqlite3'
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('PRAGMA integrity_check;')
            result = cursor.fetchone()
            conn.close()
            if not result or result[0] != 'ok':
                print("[!] Notice: Malformed SQLite database detected. Recreating clean database...")
                os.remove(db_path)
        except Exception:
            print("[!] Notice: Corrupted SQLite database detected. Recreating clean database...")
            try:
                os.remove(db_path)
            except Exception:
                pass

def main():
    """Run administrative tasks."""
    check_and_repair_sqlite_db()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        if "database disk image is malformed" in str(e).lower() or "malformed" in str(e).lower():
            print("[!] Recovering from malformed database error... Rebuilding clean database.")
            db_path = 'db.sqlite3'
            if os.path.exists(db_path):
                try:
                    os.remove(db_path)
                except Exception:
                    pass
            execute_from_command_line(sys.argv)
        else:
            raise

if __name__ == '__main__':
    main()

