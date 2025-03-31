from django import forms
from datetime import datetime
from billing.models import ProjectInfo

class CDRFilterForm(forms.Form):
  today = datetime.now().strftime("%Y-%m-%d")

  datetime_from = forms.DateTimeField(
    required=True,
    initial=f"{today} 00:00",
    widget=forms.DateTimeInput(attrs={
      'class': 'form-control datetimepicker',
      'id': 'datetimeFromPicker'
    })
  )

  datetime_to = forms.DateTimeField(
    required=True,
    initial=f"{today} 23:00",
    widget=forms.DateTimeInput(attrs={
      'class': 'form-control datetimepicker',
      'id': 'datetimeToPicker'
    })
  )

  project = forms.ChoiceField(
    required=True,
    choices=[],
    widget=forms.Select(attrs={'class': 'form-select'})
  )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    from django.db.utils import OperationalError, ProgrammingError
    try:
      choices = [(p.schema_name, p.schema_name) for p in ProjectInfo.objects.all()]
      if choices:
        self.fields['project'].choices = choices
      else:
        self.fields['project'].choices = [("", "None")]
    except (OperationalError, ProgrammingError):
      self.fields['project'].choices = [("", "None")]
