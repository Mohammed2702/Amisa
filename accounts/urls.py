from django.urls import path

from .views import (
	account_signup,
	account_signin,
	account_signout,
	account_forgot_password,
	account_forgot_password_link,
	account_dashboard,
	account_profile,
	account_users_wallet,
	toggle_permission,
	account_users_list
)

app_name = 'accounts'

urlpatterns = [
	path('dashboard/', account_dashboard, name='home'),
	path('profile/', account_profile, name='account_profile'),
	path('users/', account_users_wallet, name='account_users_wallet'),
	path('users/<str:username>', toggle_permission, name='toggle_permission'),
	path('users/<str:user_type>/', account_users_list, name='account_users_list'), #
	path('register/', account_signup, name='account_signup'),
	path('login/', account_signin, name='account_signin'),
	path('logout/', account_signout, name='account_signout'),
	path('forgot_password/', account_forgot_password, name='account_forgot_password'),
	path('forgot_password/<str:link>/', account_forgot_password_link, name='account_forgot_password_link')
]
