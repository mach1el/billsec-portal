from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.db.utils import OperationalError, ProgrammingError
from billing.models import ProjectInfo


@login_required
def project_list(request):
  """Display a list of added projects."""
  projects = ProjectInfo.objects.all()
  return render(request, 'project_list.html', {'projects': projects})


@login_required
def project_delete(request, project_id):
  """Delete a selected project by ID."""
  project = get_object_or_404(ProjectInfo, id=project_id)
  project.delete()
  messages.success(request, "✅ Project deleted successfully.")
  return redirect('projects_management:list')


@login_required
def add_project(request):
  """Add a new project (database credentials)."""
  if request.method == 'POST':
    storage = get_messages(request)
    for _ in storage:
      pass  # Clear old messages if any

    host = request.POST.get('db_host')
    port = request.POST.get('db_port')
    schema_name = request.POST.get('db_schema')
    user = request.POST.get('db_user')
    password = request.POST.get('db_password')

    try:
      if not port.isdigit():
        raise ValueError("Port must be a number.")

      port = int(port)
      if not (1 <= port <= 65535):
        raise ValueError("Port must be between 1 and 65535.")

      if not all([host, schema_name, user, password]):
        raise ValueError("All fields are required.")

      try:
        ProjectInfo.objects.create(
          host=host,
          port=port,
          schema_name=schema_name,
          user=user,
          password=password
        )
        messages.success(request, "✅ Project added successfully.")
        return redirect('projects_management:add_project')

      except (OperationalError, ProgrammingError):
        messages.error(request, "⚠️ Database table is missing. Please run 'python manage.py migrate'.")
      except Exception as e:
        messages.error(request, f"❌ Failed to add project: {str(e)}")

    except ValueError as e:
      messages.error(request, str(e))
    except Exception as e:
      messages.error(request, f"An unexpected error occurred: {str(e)}")

  return render(request, 'add_project.html')