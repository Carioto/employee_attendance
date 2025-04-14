from django.contrib import admin
from .models import AttendanceRecord  # Import AttendanceRecord model


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ["employee", "date", "code", "comment"]
    list_filter = ["date", "code"]
    search_fields = ["employee__first_name", "employee__last_name", "date"]
