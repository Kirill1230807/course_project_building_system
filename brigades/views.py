from django.shortcuts import render

# Create your views here.
def brigades(request):
    return render(request, 'brigades/brigades.html')