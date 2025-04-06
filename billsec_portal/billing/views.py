from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connections
from django.utils.timezone import make_naive
from .forms import ReportFilterForm

@login_required
def home(request):
  report_data = []
  total_charge = 0

  form = ReportFilterForm(request.POST or None)

  if request.method == "POST" and form.is_valid():
    datetime_from = form.cleaned_data['datetime_from']
    datetime_to = form.cleaned_data['datetime_to']
    project_schema = form.cleaned_data['project']

    # Handle timezone-aware datetime safely
    if datetime_from and datetime_to:
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
          charge = total_seconds * 1 * 1000  # Charge 1 VND * 1000 per second
          report_data.append({
            'carrier': carrier,
            'duration': total_seconds,
            'charge': charge
          })

        total_charge = sum(item['charge'] for item in report_data)

      except Exception as e:
        form.add_error(None, f"⚠️ Error querying project: {str(e)}")

  return render(request, 'home.html', {
    "form": form,
    "report_data": report_data,
    "total_charge": total_charge,
  })
