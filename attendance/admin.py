from django.contrib import admin
from .models import Attendance, Employee, LeaveRequest


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
	list_display = ('employee_id', 'full_name', 'department', 'role')
	search_fields = ('employee_id', 'full_name', 'department', 'role')
	list_filter = ('department', 'role')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
	list_display = ('employee', 'date', 'clock_in', 'clock_out', 'status')
	search_fields = ('employee__employee_id', 'employee__full_name')
	list_filter = ('date', 'status')


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
	list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'created_at')
	search_fields = ('employee__employee_id', 'employee__full_name', 'leave_type', 'status')
	list_filter = ('leave_type', 'status', 'start_date', 'end_date')
