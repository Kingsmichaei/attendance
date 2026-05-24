from django.shortcuts import render, redirect
from .models import Employee
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def create_employee(request):
    if request.method == "POST":
        Employee.objects.create(
            employee_id=request.POST['employee_id'],
            full_name=request.POST['full_name'],
            department=request.POST['department'],
            role=request.POST['role']
        )
        return redirect('create_employee')

    return render(request, 'accounts/create_employee.html')

