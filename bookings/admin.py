from django.contrib import admin

from .models import Booking, BookingDoctor, Payment

# Register your models here.

class BookingDoctorInLine(admin.TabularInline):
    model = BookingDoctor
    readonly_fields = ('payment', 'user', 'doctor', 'frequency', 'doctor_price', 'ordered')
    extra = 0

class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_number', 'full_name', 'phone', 'email', 'city', 'booking_total', 'tax', 'status', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['booking_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [BookingDoctorInLine]

admin.site.register(Payment)
admin.site.register(Booking, BookingAdmin)
admin.site.register(BookingDoctor)
