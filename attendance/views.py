from django.shortcuts import render
from .models import Attendance
from accounts.models import Employee
from django.utils import timezone

def attendance_page(request):
    message = ""

    if request.method == "POST":
        emp_id = request.POST['employee_id']

        try:
            employee = Employee.objects.get(employee_id=emp_id)
        except Employee.DoesNotExist:
            message = "Invalid Employee ID"
            return render(request, 'attendance/attendance.html', {'message': message})

        today = timezone.now().date()
        attendance, created = Attendance.objects.get_or_create(
            employee=employee, date=today
        )

        now = timezone.now().time()

        if not attendance.clock_in:
            attendance.clock_in = now
            attendance.status = "Late" if now.hour >= 9 else "Present"
            message = "Clock-in successful"
        elif not attendance.clock_out:
            attendance.clock_out = now
            message = "Clock-out successful"
        else:
            message = "You have already clocked out today"

        attendance.save()

    return render(request, 'attendance/attendance.html', {'message': message})

