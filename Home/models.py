from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import *
from django.dispatch import *
from django.urls import reverse
from django.template.defaultfilters import slugify
import datetime
from . import utils

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


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	reference_id = models.CharField(max_length=100, blank=False, unique=True)
	state = models.CharField(max_length=15, choices=user_location, default='Kano')
	date_joined = models.DateTimeField(default=timezone.now)
	phone_number = models.CharField(max_length=12, blank=True, default='---- --- ----')

	class Meta:
		verbose_name = "Profile"
		verbose_name_plural = "Profiles"

	def __str__(self):
		return self.user.username

	def save(self, *args, **kwargs):
		self.account_type_change_counter += 1

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

	def is_expired(self):
		if timezone.now().date() >= self.expiry_date:
			return True
		else:
			return False


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

	def get_absolute_url(self):
		return reverse('Home:post_details', args=[str(self.id)])


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


class Resolution(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	content = models.TextField(blank=False)
	date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.author.username

	class Meta:
		verbose_name = 'Resolution'
		verbose_name_plural = 'Resolutions'


class Reply(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	post = models.ForeignKey(Resolution, on_delete=models.CASCADE)
	content = models.TextField(blank=False)
	date = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return str(self.post.author) + ' ' + str(self.content)

	def get_author(self):
		author = self.author.get_full_name()
		
		return author


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
