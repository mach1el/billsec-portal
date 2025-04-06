from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.db import connections
from django.db.utils import OperationalError, ProgrammingError
from .models import ProjectInfo
from .forms import ReportFilterForm

def home(request):
  if not request.user.is_authenticated:
    return redirect('users:login')

  report_data = []
  total_charge = 0

  if request.method == "POST":
    form = ReportFilterForm(request.POST)
    if form.is_valid():
      datetime_from = form.cleaned_data['datetime_from']
      datetime_to = form.cleaned_data['datetime_to']
      project_schema = form.cleaned_data['project']

      if datetime_from and datetime_to:
        from django.utils.timezone import make_naive
        datetime_from = make_naive(datetime_from)
        datetime_to = make_naive(datetime_to)

      if project_schema:
        try:
          with connections['data_central'].cursor() as cursor:
            query = f"""
              SELECT carrier,
                    SUM(
                      CASE
                        WHEN duration < 6 THEN 6
                        ELSE duration
                      END
                    ) AS total_seconds
              FROM "{project_schema}"
              WHERE created BETWEEN %s AND %s
              GROUP BY carrier
              ORDER BY carrier ASC
            """

            cursor.execute(query, [datetime_from, datetime_to])
            rows = cursor.fetchall()

          for carrier, total_seconds in rows:
            charge = total_seconds * 1 * 1000
            report_data.append({
              'carrier': carrier,
              'duration': total_seconds,
              'charge': charge
            })

          total_charge = sum(item['charge'] for item in report_data)

        except Exception as e:
          form.add_error(None, f"Error querying project: {str(e)}")

      context = {
        "form": form,
        "datetime_from": datetime_from,
        "datetime_to": datetime_to,
        "selected_project": project_schema,
        "report_data": report_data,
        "total_charge": total_charge
      }
      return render(request, 'home.html', context)

  else:
    form = ReportFilterForm()

  return render(request, 'home.html', {"form": form})

@login_required
def add_project(request):
  if request.method == 'POST':
    storage = get_messages(request)
    for _ in storage:
      pass

    host = request.POST.get('db_host')
    port = request.POST.get('db_port')
    schema_name = request.POST.get('db_schema')
    user = request.POST.get('db_user')
    password = request.POST.get('db_password')

    try:
      if not port.isdigit():
        raise ValueError("Port must be a number.")
      
      port = int(port)
      if port < 1 or port > 65535:
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
        messages.success(request, "Project added successfully.")
        return redirect('billing:add_project')

      except (OperationalError, ProgrammingError):
        messages.error(request, "Database table is missing. Please run 'python manage.py migrate'.")

      except Exception as e:
        messages.error(request, f"Failed to add project: {str(e)}")

    except ValueError as e:
      messages.error(request, str(e))
    except Exception as e:
      messages.error(request, f"An unexpected error occurred: {str(e)}")

  return render(request, 'add_project.html')