# PulseTrack Attendance App

Modern Django attendance management app for organizations.

## Features
- Employee check-in/check-out portal
- Attendance dashboard with date and employee filters
- CSV export for reporting
- Employee directory and create/update flow
- Login/logout authentication
- Responsive modern UI with centralized static assets

## Quick Start
```bash
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

## Main Routes
- `/` Home
- `/login/` Login
- `/attendance/` Kept
- `/dashboard/` Dashboard
- `/employees/` Employees
- `/employees/new/` New Employee
