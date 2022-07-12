from django.urls import path
from . import views


urlpatterns = [
    path('confirm_booking/', views.confirm_booking, name='confirm_booking'),
    path('payments/', views.payments, name='payments'),
    path('booking_complete/', views.booking_complete, name ='booking_complete')
]