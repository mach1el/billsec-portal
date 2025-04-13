import csv
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import render
from django.db import connections
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_naive

from .forms import CDRFilterForm

class Echo:
  def write(self, value):
    return value

@login_required
def cdr_report(request):
  """Display paginated CDR report."""
  headers = []
  report_data = []

  form = CDRFilterForm(request.POST or None)

  if request.method == "POST" and form.is_valid():
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
      form.add_error(None, f"⚠️ Database error: {str(e)}")

  paginator = Paginator(report_data, 100)
  page = request.GET.get('page')

  try:
    page_data = paginator.page(page)
  except PageNotAnInteger:
    page_data = paginator.page(1)
  except EmptyPage:
    page_data = paginator.page(paginator.num_pages)

  return render(request, "cdr_report.html", {
    "form": form,
    "headers": headers,
    "page_data": page_data,
    "report_data": page_data.object_list
  })

@login_required
def export_cdr_csv(request):
  """Streaming export for CDR CSV."""
  if request.method == "POST":
    form = CDRFilterForm(request.POST)
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

          pseudo_buffer = Echo()
          writer = csv.writer(pseudo_buffer)

          def stream_rows():
            yield writer.writerow(headers)
            while True:
              row = cursor.fetchone()
              if row is None:
                break
              yield writer.writerow(row)

          response = StreamingHttpResponse(
            stream_rows(),
            content_type="text/csv"
          )
          response['Content-Disposition'] = f'attachment; filename="cdr_report_{schema}.csv"'
          return response

      except Exception as e:
        return HttpResponse(f"Error generating CSV: {str(e)}", status=500)

  return HttpResponse("Invalid request", status=400)