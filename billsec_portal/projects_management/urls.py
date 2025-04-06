from django.urls import path
from . import views

app_name = 'projects_management'

urlpatterns = [
  path('add', views.add_project, name='add_project'),
  path('projects', views.project_list, name='list'),
  path('delete/<int:project_id>/', views.project_delete, name='delete'),
]