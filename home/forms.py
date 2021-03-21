from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from . import models


class LocatorForm(forms.Form):
	id_ = forms.CharField(required=False)
	location = forms.CharField(required=False)
	information = forms.CharField(required=False)


class SiteSettingForm(forms.Form):
	customer_rate = forms.FloatField(required=False)
	minimum_withdrawal = forms.IntegerField(required=False)
	minimum_airtime = forms.IntegerField(required=False)
	minimum_data = forms.IntegerField(required=False)
	reservation_amount = forms.IntegerField(required=False)
	call_contact = forms.CharField(required=False)
	whatsapp_contact = forms.CharField(required=False)
	email_contact = forms.CharField(required=False)
	airtime_note = forms.CharField(required=False)
	data_note = forms.CharField(required=False)
	withdrawal_note = forms.CharField(required=False)
	how_to = forms.CharField(required=False)
	about_us = forms.CharField(required=False)
	terms_of_use = forms.CharField(required=False)
