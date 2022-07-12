import json
import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from team.models import Doctor
from .models import Booking, BookingDoctor, Payment
from .forms import BookingForm
from carts.models import CartItem
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Create your views here.
def confirm_booking(request, total=0, frequency=0):
    current_user = request.user

    #if the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('team')


    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.doctor.price *cart_item.frequency)
        frequency +=cart_item.frequency

    tax = (18 * total)/100
    grand_total = round(total + tax, 2)

    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():

            #store all the billing info inside order table
            data = Booking()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.country = form.cleaned_data['country']
            data.booking_note = form.cleaned_data['booking_note']
            data.booking_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save() #once saved it will create a primary key
            
            # generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            
            current_date = d.strftime("%Y%m%d") #20220710
            
            booking_number = current_date + str(data.id)
            data.booking_number = booking_number
            data.save()

            booking =  Booking.objects.get(user=current_user, is_ordered=False, booking_number=booking_number)

            context = {
                'booking' : booking,
                'cart_items' : cart_items,
                'total' : total,
                'tax' : tax,
                'grand_total' : grand_total,

            }

            return render(request, 'bookings/payments.html', context)

        else:
            return redirect('checkout')

def payments(request):
    body = json.loads(request.body)
    booking = Booking.objects.get(user = request.user, is_ordered = False, booking_number=body['orderID'])
    
    #store transaction details inside payment model
    payment = Payment(
        user =request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = booking.booking_total,
        status = body['status'],
    )

    payment.save()

    booking.payment = payment
    booking.is_ordered = True
    booking.save()

    #move the cart items to Booking Doctor table

    cart_items = CartItem.objects.filter(user = request.user)

    for item in cart_items:
        bookingdoctor = BookingDoctor()
        bookingdoctor.booking_id = booking.id
        bookingdoctor.payment = payment
        bookingdoctor.user_id = request.user.id
        bookingdoctor.doctor_id = item.doctor_id
        bookingdoctor.frequency = item.frequency
        bookingdoctor.doctor_price = item.doctor.price
        bookingdoctor.ordered = True
        bookingdoctor.save()

        cart_item = CartItem.objects.get(id=item.id)
        doctor_slot = cart_item.slots.all()
        bookingdoctor = BookingDoctor.objects.get(id=bookingdoctor.id)
        bookingdoctor.slots.set(doctor_slot)
        bookingdoctor.save()


        #reduce the no of booked slots based on frequency
        doctor = Doctor.objects.get(id=item.doctor_id)
        doctor.slots -= item.frequency
        doctor.save()


    #clear the cart
    CartItem.objects.filter(user = request.user).delete()



    #send booking confirmation email
    mail_subject = 'Thank you for your booking!'
    message = render_to_string('bookings/booking_confirmation_email.html', {
                'user': request.user,
                'booking' : booking
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()



    #send booking number and trans id back to senData method in payments.html using json
    data = {
        'booking_number': booking.booking_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


def booking_complete(request):
    booking_number = request.GET.get('booking_number')
    transID = request.GET.get('payment_id')

    #cart_items = CartItem.objects.filter(user = request.user)

    try:
        booking = Booking.objects.get(booking_number=booking_number, is_ordered=True)
        booked_doctors = BookingDoctor.objects.filter(booking_id=booking.id)
        
        sub_total =0
        for i in booked_doctors:
            sub_total += i.doctor_price * i.frequency

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'booking' : booking,
            'booked_doctors' : booked_doctors,
            'booking_number' : booking.booking_number,
            'transID': payment.payment_id,
            'payment' : payment,
            'sub_total' : sub_total,
            #'slot' : booking.doctor_slot,


        }
        return render(request, 'bookings/booking_complete.html', context)

    except (Payment.DoesNotExist, Booking.DoesNotExist):
        return redirect('home')
