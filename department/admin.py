from django.contrib import admin
from .models import Department

# Register your models here.

class DepartmentAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('dept_name',)}
    list_display = ('dept_name', 'slug')

admin.site.register(Department, DepartmentAdmin)

