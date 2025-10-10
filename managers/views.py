from django.shortcuts import render

# Create your views here.
def managers(request):
    return render(request, 'managers/managers.html')