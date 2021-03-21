from django import forms

from services.models import Advert


class DataForm(forms.Form):
	network = forms.CharField(max_length=100)
	phone_number = forms.CharField(max_length=100)
	amount = forms.IntegerField()


class WithdrawalForm(forms.Form):
	account_number = forms.IntegerField(required=True)
	account_name = forms.CharField(max_length=100, required=True)
	bank = forms.CharField(max_length=100, required=True)
	amount = forms.IntegerField()


class NetworkForm(forms.Form):
	network = forms.CharField(max_length=500, required=True)
	data_rate = forms.FloatField()


class BankForm(forms.Form):
	bank = forms.CharField(max_length=500, required=True)


class AdvertForm(forms.ModelForm):
	class Meta:
		model = Advert
		fields = ['client_fullname', 'image_file', 'priority']
