from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from accounts.models import Profile


User = get_user_model()


class RegistrationForm(UserCreationForm):
	first_name = forms.CharField(max_length=200, required=True, help_text='First name is required')
	last_name = forms.CharField(max_length=200, required=True, help_text='Last name is required')
	email = forms.EmailField(max_length=254, required=True, help_text='Email is required')

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2',)


class LoginForm(forms.Form):
	username = forms.CharField(max_length=255, required=True)
	password = forms.CharField(max_length=255, required=True, widget=forms.PasswordInput)


class UserUpdateForm(forms.ModelForm):
	first_name = forms.CharField(max_length=200, required=True, help_text='First name is required')
	last_name = forms.CharField(max_length=200, required=True, help_text='Last name is required')
	email = forms.EmailField(max_length=254, required=True, help_text='Email is required')

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'username', 'email',)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('state', 'phone_number',)

class ForgotPasswordForm(forms.Form):
	username = forms.CharField(required=True)


class VerificationForm(forms.Form):
	username = forms.CharField(required=True)
	email = forms.CharField(required=True)
	new_password = forms.CharField(required=True)
	confirm_password = forms.CharField(required=True)


class PasswordResetForm(forms.Form):
	old_password = forms.CharField(required=True)
	new_password = forms.CharField(required=True)
	confirm_password = forms.CharField(required=True)
