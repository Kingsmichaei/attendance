from django.urls import path
from .views import (
    attendance_page,
    dashboard,
    employee_create,
    employee_list,
    export_csv,
    home,
    leave_create,
    leave_list,
    my_attendance,
    my_leaves,
    portal,
    request_leave,
)

app_name = 'attendance'

urlpatterns = [
    path('', home, name='home'),
    path('attendance/', attendance_page, name='attendance_page'),
    path('kept/', attendance_page, name='attendance_kept'),
    path('portal/', portal, name='portal'),
    path('my-attendance/', my_attendance, name='my_attendance'),
    path('my-leaves/', my_leaves, name='my_leaves'),
    path('my-leaves/request/', request_leave, name='request_leave'),
    path('dashboard/', dashboard, name='attendance_dashboard'),
    path('export/', export_csv, name='attendance_export'),
    path('employees/', employee_list, name='employee_list'),
    path('employees/new/', employee_create, name='employee_create'),
    path('leaves/', leave_list, name='leave_list'),
    path('leaves/new/', leave_create, name='leave_create'),
]
