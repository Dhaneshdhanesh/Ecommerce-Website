from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser




class User(AbstractUser):

    ROLE_CHOICES = (
        ('SELLER', 'Seller'),
        ('BUYER', 'Buyer'),
    )

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=15)

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='BUYER'
    )

    def __str__(self):
        return self.username


class Product(models.Model):

    name = models.CharField(max_length=200)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True
    )

    stock = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name