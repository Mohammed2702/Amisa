from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import *
from django.views.static import serve
from django.conf.urls import url
from django.contrib.sitemaps.views import *
from django.contrib import *

from Home import sitemaps

sitemaps = {
    'posts': sitemaps.PostSitemap,
    'static': sitemaps.StaticViewSitemap
}

handler400 = 'Home.views.custom_400'
handler403 = 'Home.views.custom_403'
handler404 = 'Home.views.custom_404'
handler500 = 'Home.views.custom_500'


urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path('', include('Home.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^static_files/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    ]
else:
    urlpatterns += [
        url(r'^static_files/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    ]
