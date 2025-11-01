from django.shortcuts import render

# Create your views here.
def workplan(request):
    return render(request, 'workplan/workplan.html')