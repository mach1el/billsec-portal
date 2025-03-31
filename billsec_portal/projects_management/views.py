from django.shortcuts import render, redirect, get_object_or_404
from billing.models import ProjectInfo

def project_list(request):
  projects = ProjectInfo.objects.all()
  return render(request, 'project_list.html', {'projects': projects})

def project_delete(request, project_id):
  project = get_object_or_404(ProjectInfo, id=project_id)
  project.delete()
  return redirect('projects_management:list')
