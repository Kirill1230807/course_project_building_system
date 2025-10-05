from django.shortcuts import render

# Create your views here.
def employees(request):
    return render(request, 'employees/employees.html')