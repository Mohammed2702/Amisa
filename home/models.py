from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models.signals import *
from django.dispatch import *
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin
)
import datetime

from . import utils
from .data import user_location
from .manager import (
    UserManager,
    CodeGroupManager
)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True, blank=False)
    email = models.EmailField(max_length=50, blank=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now=True)
    last_updated = models.DateField(auto_now_add=True)

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        user = User.objects.get(username=self.username)

        profile_created, profile = Profile.objects.get_or_create(user=user)
        wallet_created, wallet = Wallet.objects.get_or_create(
            user=user,
            wallet_balance=0.0
        )

        if not profile_created:
            profile.save()

        if not wallet_created:
            wallet.save()

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reference_id = models.CharField(max_length=100, blank=True, unique=True)
    state = models.CharField(max_length=15, choices=user_location, default='N/A')
    date_joined = models.DateTimeField(default=timezone.now)
    phone_number = models.CharField(max_length=12, blank=True, default='N/A')

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.reference_id:
            exisiting_refs = Profile.objects.values_list('reference_id')

            self.reference_id = utils.generate_referrence_id(exisiting_refs)
        super().save(*args, **kwargs)


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_balance = models.FloatField(blank=True)
    wallet_status = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Wallet'
        verbose_name_plural = 'Wallets'

    def __str__(self):
        return self.user.username


class CodeGroup(models.Model):
    code_batch_number = models.CharField(max_length=100, blank=False, unique=True)
    status = models.BooleanField(default=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    date_created = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Code Group'
        verbose_name_plural = 'Code Groups'

    def __str__(self):
        return self.code_batch_number

    def save(self, *args, **kwargs):
        self.slug = slugify(self.code_batch_number)
        super().save(*args, **kwargs)

    def get_absolute_url(self, *args, **kwargs):
        return reverse('Home:code_batch_sheet', args=[self.slug])

    def create_codes(self, **kwargs):
        EXISTING_CODES = Code.objects.values_list('code')

        batch_number = CodeGroup.objects.get(code_batch_number=kwargs['code_batch_number'])
        number_of_codes = kwargs['number_of_codes']
        amount_per_code = kwargs['amount_per_code']
        # expiry_date = kwargs['expiry_date']
        expiry_date = datetime.datetime(
            year=2022,
            month=10,
            day=10,
            hour=12,
            minute=0
        )

        for i in range(int(number_of_codes)):
            # serial_number = f'{batch_number}-{i}'
            code = utils.generate_code(EXISTING_CODES)
            new_code = Code.objects.create(
                code_group=batch_number,
                code=code,
                amount=amount_per_code,
                expiry_date=expiry_date
            )
            new_code.save()


class Code(models.Model):
    code_group = models.ForeignKey(CodeGroup, on_delete=models.CASCADE)
    code = models.CharField(
        max_length=100,
        blank=False,
        unique=True,
    )
    amount = models.FloatField(default=100.00, blank=False)
    status = models.BooleanField(default=True)
    slug = models.SlugField(max_length=20, unique=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()

    class Meta:
        verbose_name = 'Code'
        verbose_name_plural = 'Codes'

    def __str__(self):
        return self.code

    def is_expired(self):
        if timezone.now() >= self.expiry_date:
            return True
        else:
            return False

    def get_serial_number(self):
        return f'AC-{self.id}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.code)
    
        super().save(*args, **kwargs)


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

order_expiry = timezone.timedelta(hours=3)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction = models.CharField(max_length=200, blank=False)
    amount = models.IntegerField(default=0)
    recipient = models.CharField(max_length=15, default='08012345678')
    description = models.CharField(max_length=100, blank=False, default='Order')
    status = models.CharField(max_length=100, default='Pending')
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


class SiteSetting(models.Model):
    site_setting = models.CharField(max_length=100, default='Setting_1', blank=True)
    customer_rate = models.FloatField(blank=True, default=15)
    services_note = models.TextField(blank=True, default='services note')
    minimum_withdrawal = models.IntegerField(blank=True, default=100)
    minimum_airtime = models.IntegerField(blank=True, default=100)
    minimum_data = models.IntegerField(blank=True, default=100)
    call_contact = models.CharField(max_length=13, blank=True)
    whatsapp_contact = models.CharField(max_length=13, blank=True)
    email_contact = models.EmailField(blank=True)
    how_to = models.TextField(blank=True)
    terms_of_use = models.TextField(blank=True)
    faq = models.TextField(blank=True)
    about_us = models.TextField(blank=True)

    def __str__(self):
        return self.site_setting

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'


class Network(models.Model):
    network = models.CharField(max_length=100, blank=False, unique=True)
    data_rate = models.FloatField(blank=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.network

    class Meta:
        verbose_name = 'Network'
        verbose_name_plural = 'Networks'

password_reset_exp = timezone.now() + timezone.timedelta(minutes=5)

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link_slug = models.CharField(max_length=100, unique=True)
    verification_code = models.CharField(max_length=6, unique=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

    def is_expired(self):
        if timezone.now() >= password_reset_exp:
            return True
        else:
            return False


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
