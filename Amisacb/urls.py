from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import *
from django.views.static import serve
from django.conf.urls import url
from django.contrib import *


handler400 = 'home.views.custom_400'
handler403 = 'home.views.custom_403'
handler404 = 'home.views.custom_404'
handler500 = 'home.views.custom_500'

STATIC_URL = settings.STATIC_URL.replace('/', '')

urlpatterns = [
    path('', include('home.urls')),
    path('', include('blog.urls'))
]

urlpatterns += [
    path('ADM-admin/', admin.site.urls),
#    path(f'{STATIC_URL}/<slug:slug>', serve,{'document_root': settings.STATIC_ROOT}),
]
