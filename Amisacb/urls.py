from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import *
from django.views.static import serve
from django.conf.urls import url
from django.contrib.sitemaps.views import *
from django.contrib import *


handler400 = 'Home.views.custom_400'
handler403 = 'Home.views.custom_403'
handler404 = 'Home.views.custom_404'
handler500 = 'Home.views.custom_500'

STATIC_URL = settings.STATIC_URL.replace('/', '')

urlpatterns = [
    path('', include('Home.urls')),
]

urlpatterns += [
    path('ADM-admin/', admin.site.urls),
    path(f'{STATIC_URL}/<slug:slug>', serve,{'document_root': settings.STATIC_ROOT}),
]
