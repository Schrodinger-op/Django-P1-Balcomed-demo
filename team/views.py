from django.shortcuts import get_object_or_404, render
from carts.models import CartItem
from carts.views import _cart_id
from department.models import Department
from .models import Doctor

# Create your views here.
def team(request, department_slug=None):
    departments = None
    doctors = None

    if department_slug != None:
        departments = get_object_or_404(Department, slug=department_slug)
        doctors = Doctor.objects.filter(department=departments, is_available=True)
        doctor_count = doctors.count()

    else:
        doctors = Doctor.objects.all().filter(is_available=True)
        doctor_count= doctors.count()
    
    
    context = {
        'doctors' : doctors,
        'doctor_count': doctor_count,
    }
    return render(request, 'team/team.html',context)


def doctor_detail(request, department_slug, doctor_slug):

    try:
        single_doctor = Doctor.objects.get(department__slug= department_slug, slug=doctor_slug)
        in_cart = CartItem.objects.filter(cart__cart_id= _cart_id(request), doctor=single_doctor).exists()

    
    except Exception as e:
        raise e

    context = {
        'single_doctor': single_doctor,
        'in_cart' : in_cart,
    }
    return render(request, 'team/doctor_detail.html', context)