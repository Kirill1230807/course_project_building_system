from django.shortcuts import render

# Create your views here.
def teams(request):
    return render(request, 'teams/teams.html')