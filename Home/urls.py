from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views


app_name = 'Home'


urlpatterns = [
	# AUTHs
	path('register/', views.account_signup, name='account_signup'),
	path('login/', views.account_signin, name='account_signin'),
	path('logout/', views.account_signout, name='account_signout'),
	path('forgot_password/', views.account_forgot_password, name='account_forgot_password'),

	# Dashboard
	path('', views.account_dashboard, name='home'),
	path('profile/', views.account_profile, name='account_profile'),
	path('users/', views.account_users_wallet, name='account_users_wallet'),
	path('users/<str:user_type>/', views.account_users_list, name='account_users_list'),

	# Code Redemption
	path('code/<int:code_id>/redeeem/', views.account_code_redeem, name='account_code_redeem'),
	path('code/<str:code>/redeeem_code/', views.account_code_redeem_code, name='account_code_redeem_code'),

	# Code
	path('code/', views.account_code, name='account_code'),
	path('code/group/<str:action_type>/<int:group_id>/', views.account_code_group, name='account_code_group'),
	path('code/new/', views.account_code_request, name='account_code_request'),
	path('code/<int:code_id>/', views.account_code_details, name='account_code_details'),
	path('code/<int:code_id>/delete/', views.account_code_delete, name='account_code_delete'),
	path('code/<int:code_id>/toggle/', views.account_code_toggle, name='account_code_toggle'),

	# Services
	path('withdrawal/', views.account_user_withdrawal, name='account_user_withdrawal'),
	path('data/', views.account_user_data, name='account_user_data'),
	path('airtime/', views.account_user_airtime, name='account_user_airtime'),

	# Extras
	path('pricing/', views.charges_and_pricing, name='charges_and_pricing'),
	path('terms/', views.terms_of_use, name='terms_of_use'),
	path('cardissunance/', views.card_issuance, name='card_issuance'),
	path('howto/', views.how_to, name='how_to'),
	path('faq/', views.faq, name='faq'),

	# Tools
	path('code_group/<int:group_id>/', views.code_group_codes, name='code_group_codes'),
	path('settings/', views.site_settings, name='site_settings'),
	path('orders/', views.show_all_orders, name='show_all_orders'),
	path('orders/<int:order_id>/toggle', views.toggle_order, name='toggle_order'),
	path('post/', views.all_posts, name='posts'),
	path('post/<int:post_id>/', views.post_detail, name='post_details'),
	path('post/<int:post_id>/edit', views.post_edit, name='post_edit'),
]
