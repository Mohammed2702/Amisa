from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=False, default='No Description')
    amount = models.CharField(max_length=10, blank=True)
    charges = models.CharField(max_length=10, blank=True)
    date = models.DateTimeField(default=timezone.now, blank=False)
    status = models.BooleanField(default=True, blank=True)

    class Meta:
        verbose_name = 'History'
        verbose_name_plural = 'Histories'

    def __str__(self):
        return self.description


class SiteSetting(models.Model):
    site_setting = models.CharField(max_length=100, default='Setting_1', blank=True)
    customer_rate = models.FloatField(blank=True, default=15)
    withdrawal_note = models.TextField(blank=True, default='withdrawal note', null=True)
    airtime_note = models.TextField(blank=True, default='airtime note', null=True)
    data_note = models.TextField(blank=True, default='data note', null=True)
    data_charges = models.PositiveIntegerField(blank=False, default=20)
    reservation_amount = models.PositiveIntegerField(blank=True, default=50)
    minimum_withdrawal = models.PositiveIntegerField(blank=True, default=100)
    minimum_airtime = models.PositiveIntegerField(blank=True, default=100)
    minimum_data = models.PositiveIntegerField(blank=True, default=100)
    call_contact = models.CharField(max_length=13, blank=True)
    whatsapp_contact = models.CharField(max_length=13, blank=True)
    email_contact = models.EmailField(blank=True)
    how_to = models.TextField(blank=True)
    terms_of_use = models.TextField(blank=True)
    about_us = models.TextField(blank=True)

    def __str__(self):
        return self.site_setting

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'
