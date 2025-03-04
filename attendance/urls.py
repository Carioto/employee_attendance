from django.urls import path
from .views import attendance_entry

app_name = 'attendance'

urlpatterns = [
    path('', attendance_entry, name='record_entry'),
]
