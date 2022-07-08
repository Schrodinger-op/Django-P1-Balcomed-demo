from tkinter import CASCADE
from django.db import models
from django.urls import reverse
from department.models import Department

# Create your models here.

class Doctor(models.Model):
    #first_name = models.CharField(max_length=50)
    #last_name = models.CharField(max_length=50)
    doctor_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    about = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to = 'photos/doctors')
    slots = models.IntegerField()
    is_available = models.BooleanField(default=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('doctor_detail', args=[self.department.slug, self.slug])

    def __str__(self):
        return self.doctor_name

class SlotManager(models.Manager):
    
    def dates(self):
        return super(SlotManager, self).filter(slot_category='date', is_active=True)

    def times(self):
        return super(SlotManager, self).filter(slot_category='time', is_active=True)

slot_category_choice = (
    ('date', 'date'),
    ('time', 'time'),
)

class Slot(models.Model):

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    slot_category = models.CharField(max_length=100, choices=slot_category_choice)
    slot_value     = models.CharField(max_length=100)
    is_active     = models.BooleanField(default=True)
    created_date   = models.DateTimeField(auto_now=True)

    objects = SlotManager()

    def __str__(self):
        return self.slot_value

