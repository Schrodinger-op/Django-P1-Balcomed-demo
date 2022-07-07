
from django.shortcuts import render
from team.models import Doctor


def home(request):
    doctors = Doctor.objects.all().filter(is_available=True)
    
    context = {
        'doctors' : doctors,
    }
    
    return render(request, 'home.html', context)