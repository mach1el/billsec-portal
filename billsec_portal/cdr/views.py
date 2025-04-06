import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db import connections
from .forms import CDRFilterForm

def cdr_report(request):
  report_data = []
  headers = []

  if request.method == "POST":
    form = CDRFilterForm(request.POST or None)
    if form.is_valid():
      datetime_from = form.cleaned_data['datetime_from']
      datetime_to = form.cleaned_data['datetime_to']
      schema = form.cleaned_data['project']

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

def export_cdr_csv(request):
  """Exports the filtered CDR report to CSV."""
  if request.method == "POST":
    form = CDRFilterForm(request.POST)
    if form.is_valid():
      datetime_from = form.cleaned_data['datetime_from']
      datetime_to = form.cleaned_data['datetime_to']
      schema = form.cleaned_data['project']

      response = HttpResponse(content_type='text/csv')
      response['Content-Disposition'] = f'attachment; filename="cdr_report_{schema}.csv"'

      writer = csv.writer(response)
      
      try:
        conn = get_data_central_connection()
        with conn.cursor() as cursor:
          cursor.execute(f"""
            SELECT * FROM "{schema}"
            WHERE created BETWEEN %s AND %s
            ORDER BY created DESC
          """, [datetime_from, datetime_to])

          headers = [col[0] for col in cursor.description]
          rows = cursor.fetchall()

        writer.writerow(headers)
        for row in rows:
          writer.writerow(row)

      except Exception as e:
        return HttpResponse(f"Error generating CSV: {str(e)}", status=500)

      return response

  return HttpResponse("Invalid request", status=400)