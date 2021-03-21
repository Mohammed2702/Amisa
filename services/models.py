from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

import secrets

from Amisacb import handlers


User = get_user_model()
order_expiry = timezone.timedelta(hours=3)


class Order(models.Model):
    ORDER_STATES = [
        ('processing', 'PROCESSING'),
        ('processed', 'PROCESSED'),
        ('declined', 'DECLINED'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction = models.CharField(max_length=200, blank=False)
    amount = models.IntegerField(default=0)
    recipient = models.CharField(max_length=15, default='08012345678')
    description = models.CharField(max_length=100, blank=False, default='Order')
    status = models.CharField(max_length=100, default='processing', choices=ORDER_STATES)
    toggle_count = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return self.user.username

    def desc(self):
        return self.user.get_full_name(), self.transaction, self.amount, self.recipient, self.description

    def is_expired(self):
        if timezone.now() >= self.date + order_expiry:
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        exsiting_slugs = Order.objects.values_list('slug')
        if not self.slug:
            slug = secrets.token_urlsafe(40)
            while slug in exsiting_slugs:
                slug = secrets.token_urlsafe(40)

            self.slug = slug

        super().save(*args, **kwargs)


class Network(models.Model):
    network = models.CharField(max_length=100, blank=False, unique=True)
    data_rate = models.FloatField(blank=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.network

    class Meta:
        verbose_name = 'Network'
        verbose_name_plural = 'Networks'


class Bank(models.Model):
    bank = models.CharField(max_length=200, blank=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.bank


class Locator(models.Model):
    location = models.CharField(max_length=200, blank=False)
    information = models.TextField()
    date = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.location

    class Meta:
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'


class Advert(models.Model):
    client_fullname = models.CharField(max_length=100, blank=False)
    image_file = models.ImageField(upload_to=handlers.advert_image_handler)
    priority = models.IntegerField(default=1)
    date = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.client_fullname

    class Meta:
        verbose_name = 'Advert'
        verbose_name_plural = 'Adverts'
