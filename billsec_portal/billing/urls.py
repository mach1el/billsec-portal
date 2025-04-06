from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
  path('home', views.home, name='home'),
]