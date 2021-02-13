from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # index
    path('blog', views.IndexView.as_view(), name='blog')
]
