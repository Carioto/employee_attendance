from django import forms
from .models import AttendanceRecord

class AttendanceEntryForm(forms.Form):
    employee_id = forms.IntegerField(widget=forms.HiddenInput)
    code = forms.ChoiceField(
        choices=AttendanceRecord.ATTENDANCE_CODES,
        required=False,
        widget=forms.Select(attrs={'class': 'border p-1 rounded'})
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 1, 'class': 'border p-1 rounded'}),
        required=False
    )
