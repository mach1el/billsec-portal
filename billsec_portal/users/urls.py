from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'users'

urlpatterns = [
  path('init-admin', views.init_admin, name='init_admin'),
  path('login', views.login_view, name='login'),
  path('logout', views.logout_view, name='logout'),
]