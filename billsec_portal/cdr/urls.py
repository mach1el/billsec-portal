from django.urls import path
from . import views

app_name = 'cdr'

urlpatterns = [
  path('cdr', views.cdr_report, name='report'),
  path('cdr/export', views.export_cdr_csv, name='export_csv'),
]
