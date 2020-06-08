from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import *
from django.dispatch import *

from . import utils

account_types = [
	('Agent', 'Agent'),
	('User', 'User'),
]


user_location = [
	("Abia", "Abia"),
	("Adamawa", "Adamawa"),
	("Akwa Ibom", "Akwa Ibom"),
	("Anambra", "Anambra"),
	("Bauchi", "Bauchi"),
	("Bayelsa", "Bayelsa"),
	("Benue", "Benue"),
	("Borno", "Borno"),
	("Cross River", "Cross River"),
	("Delta", "Delta"),
	("Ebonyi", "Ebonyi"),
	("Edo", "Edo"),
	("Ekiti", "Ekiti"),
	("Enugu", "Enugu"),
	("FCT - Abuja", "FCT - Abuja"),
	("Gombe", "Gombe"),
	("Imo", "Imo"),
	("Jigawa", "Jigawa"),
	("Kaduna", "Kaduna"),
	("Kano", "Kano"),
	("Katsina", "Katsina"),
	("Kebbi", "Kebbi"),
	("Kogi", "Kogi"),
	("Kwara", "Kwara"),
	("Lagos", "Lagos"),
	("Nasarawa", "Nasarawa"),
	("Niger", "Niger"),
	("Ogun", "Ogun"),
	("Ondo", "Ondo"),
	("Osun", "Osun"),
	("Oyo", "Oyo"),
	("Plateau", "Plateau"),
	("Rivers", "Rivers"),
	("Sokoto", "Sokoto"),
	("Taraba", "Taraba"),
	("Yobe", "Yobe"),
	("Zamfara", "Zamfara"),
]


networks = [
    ('Airtel', 'Airtel'),
    ('Glo', 'Glo'),
    ('MTN', 'MTN'),
    ('9Mobile', '9Mobile'),
]


banks = [(i, i) for i in utils.get_all_banks()]


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	reference_id = models.CharField(max_length=100, blank=False, unique=True)
	account_type = models.CharField(max_length=10, choices=account_types)
	state = models.CharField(max_length=15, choices=user_location, default='Kano')
	date_joined = models.DateTimeField(default=timezone.now)

	class Meta:
		verbose_name = "Profile"
		verbose_name_plural = "Profiles"

	def __str__(self):
		return self.user.username


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
	code_group_name = models.CharField(max_length=100, blank=False, unique=True)
	date_created = models.DateTimeField(default=timezone.now)
	status = models.BooleanField(default=True)

	class Meta:
		verbose_name = 'Code Group'
		verbose_name_plural = 'Code Groups'

	def __str__(self):
		return self.code_group_name


class Code(models.Model):
	code_group = models.ForeignKey(CodeGroup, on_delete=models.CASCADE)
	code = models.CharField(
		max_length=100,
		blank=False,
		unique=True,
	)
	amount = models.FloatField(default=100.00, blank=False)
	status = models.BooleanField(default=True)
	date_created = models.DateField(auto_now_add=True)
	expiry_date = models.DateField()

	class Meta:
		verbose_name = 'Code'
		verbose_name_plural = 'Codes'

	def __str__(self):
		return self.code


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


class Order(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	transaction = models.CharField(max_length=200, blank=False)
	amount = models.IntegerField(default=0)
	recipient = models.CharField(max_length=15, default='08012345678')
	description = models.CharField(max_length=100, blank=False, default='Order')
	status = models.CharField(max_length=100, default='Pending')
	date = models.DateTimeField(default=timezone.now)

	class Meta:
		verbose_name = 'Order'
		verbose_name_plural = 'Orders'

	def __str__(self):
		return self.user.username


class Post(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=500, blank=False)
	content = models.TextField(blank=False)
	date = models.DateField(auto_now_add=True)

	class Meta:
		verbose_name = 'Post'
		verbose_name_plural = 'Posts'

	def __str__(self):
		return self.title
