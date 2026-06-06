#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
pip install gunicorn
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py shell -c "
from django.contrib.auth.models import User 
if not User.objects.filter(username='MICHAEL').exists():
    User.objects.create_superuser(
        username='MICHAEL',
        email='kingsmichael.x@gmail.com',
        password='MICHAEL123!'
    )
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"