# Generated manually to link employees to Django auth users

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations, models
import django.db.models.deletion


def create_employee_users(apps, schema_editor):
    Employee = apps.get_model('attendance', 'Employee')
    User = apps.get_model('auth', 'User')

    for employee in Employee.objects.all():
        user, _ = User.objects.get_or_create(
            username=employee.employee_id,
            defaults={
                'is_active': True,
                'is_staff': False,
                'is_superuser': False,
                'first_name': employee.full_name.split(' ')[0] if employee.full_name else '',
            },
        )
        hashed_password = make_password(employee.employee_id)
        if user.password != hashed_password:
            user.password = hashed_password
            user.save(update_fields=['password'])
        if employee.user_id != user.id:
            employee.user_id = user.id
            employee.save(update_fields=['user'])


def unlink_employee_users(apps, schema_editor):
    Employee = apps.get_model('attendance', 'Employee')
    Employee.objects.update(user=None)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('attendance', '0002_leaverequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(create_employee_users, reverse_code=unlink_employee_users),
    ]
