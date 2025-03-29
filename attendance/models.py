from django.db import models
from restaurants.models import Employee

class AttendanceRecord(models.Model):
    ATTENDANCE_CODES = [
        ('OFF', 'Not Scheduled'),
        ('NS', 'No Show'),
        ('CO', 'Called Off With Notice'),
        ('LCO', 'Called Off Without Notice'),
        ('L', 'Late ( >10 minutes)'),
        ('XL', 'Excessively Late (>30 minutes)'),
        ('P', 'On Time'),
        ('HRO', 'Hero')
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    code = models.CharField(max_length=3, choices=ATTENDANCE_CODES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.code}"
