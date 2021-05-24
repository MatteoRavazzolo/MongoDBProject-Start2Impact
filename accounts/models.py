from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    bitcoin_wallet = models.FloatField(null=True)
    fiat_wallet = models.FloatField(null=True, default=0)

    def __str__(self):
        return str(self.name)


class Product(models.Model):
    crypto = models.CharField(max_length=200, null=True, default='BTC')

    def __str__(self):
        return self.crypto


class Order(models.Model):
    BUYINGORSELLING = (
        ('Buying', 'Buying'),
        ('Selling', 'Selling'),
        )
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    btc_value = models.FloatField(null=True)
    eur_value = models.FloatField(null=True)
    sellingorbuying = models.CharField(max_length=200, null=True, choices=BUYINGORSELLING)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=200, null=True, default='Available')

    def __str__(self):
        return self.product.crypto




