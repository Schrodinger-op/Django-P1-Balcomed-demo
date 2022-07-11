from django.db import models
from accounts.models import Account
from team.models import Doctor, Slot

# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    slots = models.ManyToManyField(Slot, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    frequency = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.doctor.price * self.frequency

    def __unicode__(self):
        return self.doctor

