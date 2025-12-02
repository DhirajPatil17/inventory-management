from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about')
    ,path('register/', views.RegisterView.as_view(), name='register')
]