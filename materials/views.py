from django.shortcuts import render

# Create your views here.
def materials(request):
    return render(request, 'materials/materials.html')