from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Cart, CartItem
from team.models import Doctor

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id) #get the doctor
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request) ) #get the cart using the cart_id present in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()

    try:
        cart_item = CartItem.objects.get(doctor=doctor, cart=cart)
        cart_item.frequency += 1 
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            doctor = doctor,
            frequency = 1,
            cart = cart,
        )
        cart_item.save()

    return redirect('cart')

def remove_cart(request, doctor_id):
    cart = Cart.objects.get(cart_id= _cart_id(request))
    doctor = get_object_or_404(Doctor, id=doctor_id)
    cart_item = CartItem.objects.get(doctor=doctor, cart=cart)
    if cart_item.frequency > 1:
        cart_item.frequency -= 1
        cart_item.save()

    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request, doctor_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    doctor = get_object_or_404(Doctor, id=doctor_id)
    cart_item = CartItem.objects.get(doctor=doctor, cart=cart)
    cart_item.delete()
    return redirect('cart')



def cart(request, total=0, frequency=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.doctor.price *cart_item.frequency)
            frequency +=cart_item.frequency

        tax = (18 * total)/100
        grand_total = round(total + tax, 2)
    except ObjectNotExist:
        pass #just ignore

    context = {
        'total' : total,
        'frequency' : frequency,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
    }
    return render(request, 'team/cart.html', context)


