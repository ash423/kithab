from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

import orders.models


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state}, {self.pincode}, {self.country}"# Create your models here.

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def str(self):
        return f"{self.user.username}'s Wallet: {self.balance}"

class WalletTransaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20, choices=(
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),

    ))

    def __str__(self):
        return f"Wallet Transaction: {self.amount} - {self.date}"