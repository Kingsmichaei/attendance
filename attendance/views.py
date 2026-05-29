import csv
from datetime import date
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Attendance, Employee, LeaveRequest


staff_required = user_passes_test(
    lambda user: user.is_authenticated and user.is_staff,
    login_url='login',
)


def get_employee_for_user(user):
    return getattr(user, 'employee_profile', None)

def attendance_page(request):
    if request.method == "POST":
        emp_id = request.POST.get('employee_id', '').strip().upper()
        if not emp_id:
            messages.error(request, "Employee ID is required.")
            return redirect('attendance:attendance_page')

        try:
            employee = Employee.objects.get(employee_id=emp_id)
        except Employee.DoesNotExist:
            messages.error(request, "Employee ID not found.")
            return redirect('attendance:attendance_page')

        today = timezone.now().date()
        attendance, _ = Attendance.objects.get_or_create(
            employee=employee, date=today
        )

        now = timezone.now().time()

        if not attendance.clock_in:
            attendance.clock_in = now
            attendance.status = "Late" if now.hour >= 9 else "Present"
            messages.success(request, f"Clock-in recorded for {employee.full_name}.")
        elif not attendance.clock_out:
            attendance.clock_out = now
            messages.success(request, f"Clock-out recorded for {employee.full_name}.")
        else:
            messages.info(request, "Clock-in and clock-out are already completed for today.")

        attendance.save()
        return redirect('attendance:attendance_page')

    today_records = (
        Attendance.objects.select_related('employee')
        .filter(date=timezone.now().date())
        .order_by('-clock_in')[:15]
    )
    return render(request, 'attendance/attendance.html', {'today_records': today_records})


def home(request):
    today = timezone.now().date()
    context = {
        'today': today,
        'employee_count': Employee.objects.count(),
        'present_count': Attendance.objects.filter(date=today).exclude(clock_in__isnull=True).count(),
        'late_count': Attendance.objects.filter(date=today, status='Late').count(),
    }
    return render(request, 'home.html', context)


def favicon(request):
    favicon_path = Path(settings.MEDIA_ROOT) / 'favicon.svg'
    if favicon_path.exists():
        return HttpResponse(favicon_path.read_text(encoding='utf-8'), content_type='image/svg+xml')
    return HttpResponse(status=404)


@login_required(login_url='login')
def portal(request):
    if request.user.is_staff:
        return redirect('attendance:attendance_dashboard')

    employee = get_employee_for_user(request.user)
    if not employee:
        messages.error(request, 'No employee profile is linked to this account.')
        return redirect('logout')

    today = timezone.now().date()
    context = {
        'employee': employee,
        'today': today,
        'attendance_today': Attendance.objects.filter(employee=employee, date=today).first(),
        'recent_attendance': Attendance.objects.filter(employee=employee).order_by('-date', '-clock_in')[:8],
        'recent_leaves': LeaveRequest.objects.filter(employee=employee).order_by('-created_at')[:8],
        'my_pending_leave_count': LeaveRequest.objects.filter(employee=employee, status='Pending').count(),
    }
    return render(request, 'attendance/portal.html', context)


@staff_required
def dashboard(request):
    emp_id = request.GET.get('employee_id', '').strip().upper()
    selected_date = request.GET.get('date') or str(date.today())

    records = Attendance.objects.select_related('employee').order_by('-date', '-clock_in')
    if emp_id:
        records = records.filter(employee__employee_id=emp_id)
    if selected_date:
        records = records.filter(date=selected_date)

    context = {
        'records': records[:100],
        'filter_id': emp_id,
        'selected_date': selected_date,
    }
    return render(request, 'attendance/dashboard.html', context)


@staff_required
def export_csv(request):
    emp_id = request.GET.get('employee_id', '').strip().upper()
    selected_date = request.GET.get('date', '').strip()

    records = Attendance.objects.select_related('employee').order_by('-date')
    if emp_id:
        records = records.filter(employee__employee_id=emp_id)
    if selected_date:
        records = records.filter(date=selected_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['employee_id', 'full_name', 'date', 'clock_in', 'clock_out', 'status'])
    for r in records:
        writer.writerow([
            r.employee.employee_id,
            r.employee.full_name,
            r.date,
            r.clock_in or '',
            r.clock_out or '',
            r.status,
        ])

    return response


@staff_required
def employee_list(request):
    query = request.GET.get('q', '').strip()
    employees = Employee.objects.all()
    if query:
        employees = employees.filter(full_name__icontains=query) | employees.filter(employee_id__icontains=query)

    context = {
        'employees': employees.order_by('full_name'),
        'query': query,
    }
    return render(request, 'attendance/employees.html', context)


@staff_required
def employee_create(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id', '').strip().upper()
        full_name = request.POST.get('full_name', '').strip()
        department = request.POST.get('department', '').strip()
        role = request.POST.get('role', '').strip()
        password = request.POST.get('password', '').strip() or employee_id

        if not all([employee_id, full_name, department, role]):
            messages.error(request, 'All fields are required.')
            return redirect('attendance:employee_create')

        account, _ = User.objects.get_or_create(username=employee_id, defaults={'first_name': full_name.split(' ')[0] if full_name else ''})
        if password:
            account.set_password(password)
        account.is_active = True
        account.save()

        employee, created = Employee.objects.get_or_create(
            employee_id=employee_id,
            defaults={
                'user': account,
                'full_name': full_name,
                'department': department,
                'role': role,
            },
        )

        if not employee.user:
            employee.user = account
            employee.save(update_fields=['user'])

        if created:
            messages.success(request, f'Employee {employee.full_name} created.')
        else:
            employee.full_name = full_name
            employee.department = department
            employee.role = role
            employee.save()
            messages.info(request, f'Employee {employee.employee_id} already existed and was updated.')

        messages.success(request, f'Login credentials: username={employee.employee_id}, password={password}')
        return redirect('attendance:employee_list')

    return render(request, 'attendance/employee_form.html')


@staff_required
def leave_list(request):
    employee_id = request.GET.get('employee_id', '').strip().upper()
    status = request.GET.get('status', '').strip()

    leaves = LeaveRequest.objects.select_related('employee').all()
    if employee_id:
        leaves = leaves.filter(employee__employee_id=employee_id)
    if status:
        leaves = leaves.filter(status=status)

    context = {
        'leaves': leaves[:150],
        'filter_employee_id': employee_id,
        'filter_status': status,
        'status_choices': [choice[0] for choice in LeaveRequest.STATUS_CHOICES],
    }
    return render(request, 'attendance/leaves.html', context)


@staff_required
def leave_create(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id', '').strip().upper()
        leave_type = request.POST.get('leave_type', 'Annual').strip()
        start_date = request.POST.get('start_date', '').strip()
        end_date = request.POST.get('end_date', '').strip()
        reason = request.POST.get('reason', '').strip()

        if not all([employee_id, start_date, end_date]):
            messages.error(request, 'Employee ID, start date, and end date are required.')
            return redirect('attendance:leave_create')

        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            messages.error(request, 'Employee ID not found.')
            return redirect('attendance:leave_create')

        if leave_type not in dict(LeaveRequest.LEAVE_TYPE_CHOICES):
            leave_type = 'Annual'

        if end_date < start_date:
            messages.error(request, 'End date cannot be earlier than start date.')
            return redirect('attendance:leave_create')

        LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
        )
        messages.success(request, 'Leave request submitted successfully.')
        return redirect('attendance:leave_list')

    context = {
        'leave_types': [choice[0] for choice in LeaveRequest.LEAVE_TYPE_CHOICES],
    }
    return render(request, 'attendance/leave_form.html', context)


@login_required(login_url='login')
def request_leave(request):
    if request.user.is_staff:
        return redirect('attendance:leave_create')

    employee = get_employee_for_user(request.user)
    if not employee:
        messages.error(request, 'No employee profile is linked to this account.')
        return redirect('logout')

    if request.method == 'POST':
        leave_type = request.POST.get('leave_type', 'Annual').strip()
        start_date = request.POST.get('start_date', '').strip()
        end_date = request.POST.get('end_date', '').strip()
        reason = request.POST.get('reason', '').strip()

        if not all([start_date, end_date]):
            messages.error(request, 'Start date and end date are required.')
            return redirect('attendance:request_leave')

        if leave_type not in dict(LeaveRequest.LEAVE_TYPE_CHOICES):
            leave_type = 'Annual'

        if end_date < start_date:
            messages.error(request, 'End date cannot be earlier than start date.')
            return redirect('attendance:request_leave')

        LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
        )
        messages.success(request, 'Your leave request has been submitted.')
        return redirect('attendance:my_leaves')

    context = {
        'leave_types': [choice[0] for choice in LeaveRequest.LEAVE_TYPE_CHOICES],
        'employee': employee,
    }
    return render(request, 'attendance/request_leave.html', context)


@login_required(login_url='login')
def my_attendance(request):
    if request.user.is_staff:
        return redirect('attendance:attendance_dashboard')

    employee = get_employee_for_user(request.user)
    if not employee:
        messages.error(request, 'No employee profile is linked to this account.')
        return redirect('logout')

    records = Attendance.objects.filter(employee=employee).order_by('-date', '-clock_in')
    return render(request, 'attendance/my_attendance.html', {'employee': employee, 'records': records[:50]})


@login_required(login_url='login')
def my_leaves(request):
    if request.user.is_staff:
        return redirect('attendance:leave_list')

    employee = get_employee_for_user(request.user)
    if not employee:
        messages.error(request, 'No employee profile is linked to this account.')
        return redirect('logout')

    leaves = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')
    return render(request, 'attendance/my_leaves.html', {'employee': employee, 'leaves': leaves})


