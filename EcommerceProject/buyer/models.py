from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.utils import timezone

from seller.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()


# CART

class Cart(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


# CART ITEM

class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name='unique_product_in_cart'
            )
        ]

    def subtotal(self):

        return self.product.price * self.quantity


# ORDER

class Order(models.Model):

    STATUS_CHOICES = [

        ('PENDING', 'Pending'),

        ('CONFIRMED', 'Confirmed'),

        ('SHIPPED', 'Shipped'),

        ('DELIVERED', 'Delivered'),

        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    address = models.TextField()

    phone = models.CharField(max_length=15)

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    payment_method = models.CharField(
        max_length=30,
        default='COD'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id}"


# ORDER ITEM

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def subtotal(self):

        return self.price * self.quantity