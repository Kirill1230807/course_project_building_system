from django.shortcuts import render

# Create your views here.
def plots(request):
    return render(request, 'plots/plots.html')