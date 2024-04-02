from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager


class Customer(AbstractUser):
    username = models.CharField(max_length=30,unique=True )
    email = models.EmailField(blank=False,unique=True)
    is_verified = models.BooleanField(default=False)
    number = models.CharField(max_length=10,null=True)
    profile_photo = models.ImageField(upload_to="products", null=True, blank=True)


    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class Category(models.Model):
    category_name = models.CharField(max_length=100,unique=True)
    description = models.CharField(max_length=1000, default="")
    image = models.ImageField(upload_to="products")
    category_offer_description = models.CharField(max_length=100, null=True, blank=True)
    category_offer = models.PositiveBigIntegerField(default=0)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    product_name = models.CharField(max_length=100,unique=True)
    description = models.CharField(max_length=1000, default="")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    image = models.ImageField(upload_to="products")
    available = models.BooleanField(default=True)
    # avilable=models.BooleanField(default=False)
    product_offer = models.PositiveBigIntegerField(default=0, null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.product_name