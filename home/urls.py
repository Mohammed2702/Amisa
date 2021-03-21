from django.urls import path
from . import views

app_name = 'Home'


urlpatterns = [
	# Index
	path('', views.index, name='index'),

	# Extras
	path('pricing/', views.charges_and_pricing, name='charges_and_pricing'),
	path('terms/', views.terms_of_use, name='terms_of_use'),
	path('locator/', views.locator, name='locator'),

	# Tools
	path('code_group/<slug:group_slug>/', views.code_group_codes, name='code_group_codes'),
	path('settings/', views.site_settings, name='site_settings'),
]
