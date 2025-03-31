from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
  path('home', views.home, name='home'),
  path('add-project', views.add_project, name='add_project'),
]