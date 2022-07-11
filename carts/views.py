from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Cart, CartItem
from team.models import Doctor, Slot
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, doctor_id):

    current_user = request.user
    doctor = Doctor.objects.get(id=doctor_id) #get the doctor

    #if the user is authenticated
    if current_user.is_authenticated:

        doctor_slot = []    #get the doctor slot

        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    slot = Slot.objects.get(doctor=doctor, slot_category__iexact=key, slot_value__iexact=value)
                    doctor_slot.append(slot)

                except:
                    pass


        is_cart_item_exists = CartItem.objects.filter(doctor=doctor, user=current_user).exists()

        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(doctor=doctor, user=current_user)
            # existing_slots -> database
            # current slot -> doctor_variation
            # item_id -> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_slot = item.slots.all()
                ex_var_list.append(list(existing_slot))
                id.append(item.id)

            if doctor_slot in ex_var_list:
                # increase the cart item frequency
                index = ex_var_list.index(doctor_slot)
                item_id = id[index]
                item = CartItem.objects.get(doctor=doctor, id=item_id)
                item.frequency += 1
                item.save()

            else:
                item = CartItem.objects.create(doctor=doctor, frequency=1, user=current_user)
                if len(doctor_slot) > 0:
                    item.slots.clear()
                    item.slots.add(*doctor_slot)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                doctor = doctor,
                frequency = 1,
                user = current_user,
            )
            if len(doctor_slot)>0:
                cart_item.slots.clear()
                for item in doctor_slot:
                    cart_item.slots.add(item)
            
            cart_item.save()
        return redirect('cart')

    #if the user is not authenticated
    else:

        doctor_slot = []    #get the doctor slot
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    slot = Slot.objects.get(doctor=doctor, slot_category__iexact=key, slot_value__iexact=value)
                    doctor_slot.append(slot)

                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request) ) #get the cart using the cart_id present in the session
        
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(doctor=doctor, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(doctor=doctor, cart=cart)
            # existing_slots -> database
            # current slot -> doctor_variation
            # item_id -> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_slot = item.slots.all()
                ex_var_list.append(list(existing_slot))
                id.append(item.id)

            print(ex_var_list)

            if doctor_slot in ex_var_list:
                # increase the cart item frequency
                index = ex_var_list.index(doctor_slot)
                item_id = id[index]
                item = CartItem.objects.get(doctor=doctor, id=item_id)
                item.frequency += 1
                item.save()

            else:
                item = CartItem.objects.create(doctor=doctor, frequency=1, cart=cart)
                if len(doctor_slot) > 0:
                    item.slots.clear()
                    item.slots.add(*doctor_slot)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                doctor = doctor,
                frequency = 1,
                cart = cart,
            )
            if len(doctor_slot)>0:
                cart_item.slots.clear()
                for item in doctor_slot:
                    cart_item.slots.add(item)
            
            cart_item.save()
        return redirect('cart')

def remove_cart(request, doctor_id, cart_item_id):
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(doctor=doctor, user=request.user, id=cart_item_id)

        else:
            cart = Cart.objects.get(cart_id= _cart_id(request))
            cart_item = CartItem.objects.get(doctor=doctor, cart=cart, id=cart_item_id)
        
        if cart_item.frequency > 1:
            cart_item.frequency -= 1
            cart_item.save()

        else:
            cart_item.delete()

    except:
        pass
    return redirect('cart')

def remove_cart_item(request, doctor_id, cart_item_id):
    
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(doctor=doctor, user=request.user, id=cart_item_id)

    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(doctor=doctor, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')



def cart(request, total=0, frequency=0, cart_items=None):
    try:
        tax=0,
        grand_total=0

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            
        for cart_item in cart_items:
            total += (cart_item.doctor.price *cart_item.frequency)
            frequency +=cart_item.frequency

        tax = (18 * total)/100
        grand_total = round(total + tax, 2)
    
    except ObjectDoesNotExist:
        pass #just ignore

    context = {
        'total' : total,
        'frequency' : frequency,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
    }
    return render(request, 'team/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, frequency=0, cart_items=None):
    try:
        tax=0,
        grand_total=0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.doctor.price *cart_item.frequency)
            frequency +=cart_item.frequency

        tax = (18 * total)/100
        grand_total = round(total + tax, 2)
    
    except ObjectDoesNotExist:
        pass #just ignore

    context = {
        'total' : total,
        'frequency' : frequency,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total' : grand_total,
    }

    return render(request, 'team/checkout.html', context)