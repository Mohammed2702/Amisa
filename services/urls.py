from django.urls import path

from services.views import (
    show_all_orders,
    toggle_order,
    account_user_withdrawal,
    account_user_data,
    account_user_airtime,
    adverts,
    advert_delete,
    adverts_list
)

app_name = 'services'

urlpatterns = [
    path('orders/', show_all_orders, name='show_all_orders'),
    path('orders/<slug:order_slug>/toggle/', toggle_order, name='toggle_order'),
    path('withdrawal/', account_user_withdrawal, name='account_user_withdrawal'),
    path('data/', account_user_data, name='account_user_data'),
    path('airtime/', account_user_airtime, name='account_user_airtime'),
    path('adverts/', adverts, name='adverts'),
    path('adverts/all/', adverts_list, name='adverts_list'),
    path('adverts/<slug:slug>/delete/', advert_delete, name='advert_delete')
]
