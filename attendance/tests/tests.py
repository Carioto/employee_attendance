from django.test import TestCase
from django.contrib.auth import get_user_model
from restaurants.models import Employee, Restaurant
from attendance.models import AttendanceRecord
from django.utils import timezone

User = get_user_model()


class AttendanceModelTest(TestCase):

    def setUp(self):
        # Create a restaurant
        self.restaurant = Restaurant.objects.create(name="Testaurant")

        # Create a user and employee
        self.user = User.objects.create_user(username="gm1", password="pass", role="gm")
        self.employee = Employee.objects.create(
            first_name="John", last_name="Doe", restaurant=self.restaurant
        )

        # Assign the restaurant to the user if applicable
        self.user.restaurant = self.restaurant
        self.user.save()

    def test_create_attendance_record(self):
        today = timezone.now().date()
        record = AttendanceRecord.objects.create(
            employee=self.employee, date=today, code="P"
        )
        self.assertEqual(record.employee, self.employee)
        self.assertEqual(record.code, "P")
        self.assertEqual(record.date, today)
        record_test = AttendanceRecord.objects.get(employee=self.employee, date=today)
        self.assertEqual(record_test.code, "P")
