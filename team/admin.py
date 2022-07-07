from django.contrib import admin
from .models  import Doctor

# Register your models here.

class DoctorAdmin(admin.ModelAdmin):
    list_display = ('doctor_name', 'price', 'slots', 'department', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('doctor_name',)}


admin.site.register(Doctor,DoctorAdmin)
