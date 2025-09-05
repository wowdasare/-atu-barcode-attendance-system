#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Add the parent directory to Python path so we can import attendance_project
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_project.attendance_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)