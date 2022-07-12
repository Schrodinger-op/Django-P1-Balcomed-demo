from typing import OrderedDict
from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'city', 'state', 'country', 'booking_note']
