from django.db import models
from offbeatapp.models import Product, Customer
from shop.models import Address
from datetime import date


class Cart(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True
    )
    quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to="products", null=True, blank=True)
    device = models.CharField(max_length=255, null=True, blank=True)

    @property
    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return (
            f"Cart: {self.user.username} - {self.product} - Quantity: {self.quantity}"
        )


class Wishlist(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products", null=True, blank=True)
    device = models.CharField(max_length=255, null=True, blank=True)
    delivered_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Wishlist:{self.user.username}-{self.product}"


class Order(models.Model):
    ORDER_STATUS = (
        ("pending", "Pending"),
        ("processing", "processing"),
        ("shipped", "shipped"),
        ("delivered", "delivered"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("refunded", "refunded"),
        ("on_hold", "on_hold"),
    )

    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True
    )
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=50, null=False)
    status = models.CharField(max_length=100, choices=ORDER_STATUS, default="pending")
    quantity = models.IntegerField(default=0, null=True, blank=True)
    image = models.ImageField(upload_to="products", null=True, blank=True)
    date = models.DateField(default=date.today)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.product}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    image = models.ImageField(upload_to="products", null=True, blank=True)

    def __str__(self):
        return str(self.id)

class Coupon(models.Model):
    coupon_code=models.CharField(max_length=10)
    is_expired=models.BooleanField(default=False)
    discount_price=models.IntegerField(default=100)
    minimum_amount=models.IntegerField(default=500)
    status = models.BooleanField(default=True)

    def __str__(self):
        return str(self.coupon_code)

class Wallet(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def _str_(self):
        return f"Wallet for {self.user.username}"

class Payment(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    discount = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_method
