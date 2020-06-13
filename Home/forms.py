from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from . import models


class RegistrationForm(UserCreationForm):
	first_name = forms.CharField(max_length=200, required=True, help_text='First name is required')
	last_name = forms.CharField(max_length=200, required=True, help_text='Last name is required')
	email = forms.EmailField(max_length=254, required=True, help_text='Email is required')

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2',)


class UserUpdateForm(forms.ModelForm):
	first_name = forms.CharField(max_length=200, required=True, help_text='First name is required')
	last_name = forms.CharField(max_length=200, required=True, help_text='Last name is required')
	email = forms.EmailField(max_length=254, required=True, help_text='Email is required')

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'username', 'email',)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = models.Profile
        fields = ('state', 'account_type', 'phone_number',)


class CodeGroupForm(forms.ModelForm):
	class Meta:
		model = models.CodeGroup
		fields = ('code_group_name',)


class CodeForm(forms.Form):
	code_group = forms.CharField(max_length=100, required=True)
	code = forms.CharField(max_length=100)
	amount = forms.IntegerField()
	expiry_date = forms.CharField(max_length=100, required=True)


class DataForm(forms.Form):
	network = forms.CharField(max_length=100)
	phone_number = forms.CharField(max_length=100)
	amount = forms.IntegerField()


class CodeRedeemForm(forms.Form):
	code = forms.CharField(max_length=100)


class WithdrawalForm(forms.Form):
	account_number = forms.IntegerField(required=True)
	account_name = forms.CharField(max_length=100, required=True)
	bank = forms.CharField(max_length=100, required=True)
	amount = forms.IntegerField()


class PostForm(forms.Form):
	post_title = forms.CharField(max_length=500, required=True)
	post_content = forms.CharField(max_length=1000, required=True)


class SiteSettingForm(forms.Form):
	customer_rate = forms.FloatField(required=False)
	agent_rate = forms.FloatField(required=False)
	minimum_withdrawal = forms.IntegerField(required=False)
	minimum_airtime = forms.IntegerField(required=False)
	minimum_data = forms.IntegerField(required=False)
	call_contact = forms.CharField(required=False)
	whatsapp_contact = forms.CharField(required=False)
	email_contact = forms.CharField(required=False)
	services_note = forms.CharField(required=False)


class NetworkForm(forms.Form):
	network = forms.CharField(max_length=500, required=True)
	data_rate = forms.FloatField()


class ForgotPasswordForm(forms.Form):
	username = forms.CharField(required=True)


class VerificationForm(forms.Form):
	username = forms.CharField(required=True)
	email = forms.CharField(required=True)
	new_password = forms.CharField(required=True)
	confirm_password = forms.CharField(required=True)
