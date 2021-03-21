from django import forms

from codes.models import (
	CodeGroup
)


class CodeGroupForm(forms.ModelForm):
	number_of_codes = forms.IntegerField()
	amount_per_code = forms.IntegerField()
	expiry_date = forms.CharField()

	class Meta:
		model = CodeGroup
		fields = [
			'code_batch_number',
			'number_of_codes',
			'amount_per_code',
			'expiry_date'
		]


class CodeForm(forms.Form):
	code_group = forms.CharField(max_length=100, required=True)
	code = forms.CharField(max_length=100)
	amount = forms.IntegerField()
	expiry_date = forms.CharField(max_length=100, required=True)


class CodeRedeemForm(forms.Form):
	code = forms.CharField(max_length=100)
