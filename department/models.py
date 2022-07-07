from django.db import models
from django.urls import reverse

# Create your models here.

class Department(models.Model):
    dept_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    dept_image = models.ImageField(upload_to= 'photos/department/', blank=True)

    def get_url(self):
        return reverse('doctors_by_department', args=[self.slug])

    def __str__(self):
        return self.dept_name
