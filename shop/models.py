from django.db import models
from offbeatapp.models import Product, Customer

class Images(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    images = models.ImageField(upload_to="products")

class Profile(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    number = models.CharField(max_length=10)
    referral_code = models.CharField(max_length=10, unique=True)
    referral_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

class Address(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=False, blank=True)
    last_name = models.CharField(max_length=50, null=False, blank=True)
    email = models.EmailField()
    number = models.CharField(max_length=10)
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200)
    country = models.CharField(max_length=15)
    state = models.CharField(max_length=15)
    city = models.CharField(max_length=15)
    zip_code = models.IntegerField()
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)
