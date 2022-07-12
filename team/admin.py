from django.contrib import admin
from .models  import Doctor, Slot

# Register your models here.

class DoctorAdmin(admin.ModelAdmin):
    list_display = ('doctor_name', 'price', 'slots', 'department', 'modified_date', 'is_available')
    list_editable = ('slots', 'is_available','price')
    prepopulated_fields = {'slug': ('doctor_name',)}

class SlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'slot_category', 'slot_value', 'is_active')
    list_editable = ('slot_value', 'is_active',)
    list_filter =  ('doctor', 'slot_category', 'slot_value')

admin.site.register(Doctor,DoctorAdmin)
admin.site.register(Slot, SlotAdmin)
