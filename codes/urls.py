from django.urls import path

from codes import views

app_name = 'codes'

urlpatterns = [
	path('code/', views.account_code, name='account_code'),
	path('code/group/<str:action_type>/<slug:group_slug>/', views.account_code_group, name='account_code_group'),
	path('code/new/', views.account_code_request, name='account_code_request'),
	path('code/<slug:code_slug>/', views.account_code_details, name='account_code_details'),
	path('code/<slug:code_slug>/delete/', views.account_code_delete, name='account_code_delete'),
	path('code/<slug:code_slug>/toggle/', views.account_code_toggle, name='account_code_toggle'),
	path('code/batch/<slug:slug>/', views.code_batch_sheet, name='code_batch_sheet'),
	path('code/batch/<slug:page>/download/', views.html_to_pdf_view, name='batch_sheet_download'),
]
