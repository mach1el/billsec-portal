import csv
from django.http import HttpResponse
from django.shortcuts import render
from django.db import connections
from django.contrib.auth.decorators import login_required
from .forms import CDRFilterForm
from django.utils.timezone import make_naive

@login_required
def cdr_report(request):
  report_data = []
  headers = []

  if request.method == "POST":
    form = CDRFilterForm(request.POST)
    if form.is_valid():
      datetime_from = form.cleaned_data['datetime_from']
      datetime_to = form.cleaned_data['datetime_to']
      schema = form.cleaned_data['project']

      # Ensure datetime is naive (remove timezone info)
      if datetime_from and datetime_to:
        datetime_from = make_naive(datetime_from)
        datetime_to = make_naive(datetime_to)

      try:
        with connections['data_central'].cursor() as cursor:
          cursor.execute(f"""
            SELECT * FROM "{schema}"
            WHERE created BETWEEN %s AND %s
            ORDER BY created DESC
          """, [datetime_from, datetime_to])

          headers = [col[0] for col in cursor.description]
          report_data = cursor.fetchall()

      except Exception as e:
        form.add_error(None, f"Database error: {str(e)}")
  else:
    form = CDRFilterForm()

  return render(request, "cdr_report.html", {
    "form": form,
    "headers": headers,
    "report_data": report_data
  })


@login_required
def export_cdr_csv(request):
  """Exports the filtered CDR report to CSV."""
  if request.method == "POST":
    form = CDRFilterForm(request.POST)
    if form.is_valid():
      datetime_from = form.cleaned_data['datetime_from']
      datetime_to = form.cleaned_data['datetime_to']
      schema = form.cleaned_data['project']

      # Ensure datetime is naive (remove timezone info)
      if datetime_from and datetime_to:
        datetime_from = make_naive(datetime_from)
        datetime_to = make_naive(datetime_to)

      response = HttpResponse(content_type='text/csv')
      response['Content-Disposition'] = f'attachment; filename="cdr_report_{schema}.csv"'

      writer = csv.writer(response)

      try:
        with connections['data_central'].cursor() as cursor:
          cursor.execute(f"""
            SELECT * FROM "{schema}"
            WHERE created BETWEEN %s AND %s
            ORDER BY created DESC
          """, [datetime_from, datetime_to])

          headers = [col[0] for col in cursor.description]
          rows = cursor.fetchall()

        # Write header and rows to CSV
        writer.writerow(headers)
        for row in rows:
          writer.writerow(row)

      except Exception as e:
        return HttpResponse(f"Error generating CSV: {str(e)}", status=500)

      return response

  return HttpResponse("Invalid request", status=400)
