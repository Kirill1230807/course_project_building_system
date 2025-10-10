from django.shortcuts import render

# Create your views here.
def type_of_work(request):
    return render(request, 'type_of_work/type_of_work.html')