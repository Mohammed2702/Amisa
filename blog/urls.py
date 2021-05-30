from django.urls import path
from blog import views

app_name = 'blog'

urlpatterns = [
    path('blog', views.IndexView.as_view(), name='blog'),
    path('blog/<slug:slug>/', views.PostDetails.as_view(), name='blog-details')
]
