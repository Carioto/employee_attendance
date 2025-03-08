from django.urls import path
from . import views

app_name = 'reports'  # This fixes the namespace issue

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('weekly-compliance/', views.weekly_compliance_report, name='weekly_compliance_report'),
    path('monthly-attendance/', views.monthly_attendance_summary, name='monthly_attendance_summary')
]
