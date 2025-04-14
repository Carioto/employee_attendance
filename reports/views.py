from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from attendance.models import AttendanceRecord
from restaurants.models import Employee
from calendar import monthrange


def get_mondays():
    """Generate a list of Monday dates for the dropdown."""
    today = datetime.today()
    mondays = [
        (today - timedelta(days=today.weekday()) - timedelta(weeks=i)).strftime(
            "%Y-%m-%d"
        )
        for i in range(10)
    ]
    return sorted(mondays, reverse=True)


def get_user_restaurants(user):
    if user.role == "dm":
        return user.restaurants.all()
    elif user.restaurant:
        return [user.restaurant]
    return []


# Point values for attendance violations
ATTENDANCE_POINTS = {
    "NS": 3,  # No call no show
    "LCO": 2,  # Calling Off Without Notice
    "CO": 1,  # Calling Off with Notice
    "L": 0.5,  # Late (>10 minutes)
    "XL": 1,  # Excessively Late (>30 minutes)
    "P": 0,  # Present
    "HRO": -1,  # Hero (extra shift incentive)
}


@login_required
def reports_home(request):
    return render(request, "reports/reports_home.html")


@login_required
def weekly_compliance_report(request):
    mondays = get_mondays()
    selected_week = request.GET.get("week", mondays[0])  # Default to most recent Monday
    start_date = datetime.strptime(selected_week, "%Y-%m-%d")
    end_date = start_date + timedelta(days=6)
    two_months_ago = start_date - timedelta(days=60)

    restaurants = get_user_restaurants(request.user)

    # Fetch attendance records for the selected week
    weekly_attendance = AttendanceRecord.objects.filter(
        date__range=[start_date, end_date], employee__restaurant__in=restaurants
    )

    # Fetch attendance records for the past 2 months
    two_months_attendance = AttendanceRecord.objects.filter(
        date__range=[two_months_ago, end_date], employee__restaurant__in=restaurants
    )

    employees = {}

    for entry in weekly_attendance:
        if entry.employee.id not in employees:
            employees[entry.employee.id] = {
                "name": f"{entry.employee.first_name} {entry.employee.last_name}",
                "first_name": entry.employee.first_name,  # Store first name for sorting
                "codes": {
                    day: {"code": "", "color": "", "comment": ""}
                    for day in [
                        "monday",
                        "tuesday",
                        "wednesday",
                        "thursday",
                        "friday",
                        "saturday",
                        "sunday",
                    ]
                },
                "point_total": 0,  # Initialize point total
                "weekly_compliance": 0,  # Initialize weekly compliance percentage
            }

        weekday = entry.date.strftime("%A").lower()  # Get weekday name in lowercase
        employees[entry.employee.id]["codes"][weekday] = {
            "code": entry.code,  # The attendance code
            "color": "",  # Placeholder for color logic (to be added later)
            "comment": (
                entry.comment if entry.comment else ""
            ),  # Pass the comment to the template
        }

    # Calculate 2-month point total
    for entry in two_months_attendance:
        if entry.employee.id in employees and entry.code in ATTENDANCE_POINTS:
            employees[entry.employee.id]["point_total"] += ATTENDANCE_POINTS[entry.code]

    # Calculate weekly compliance percentage
    for employee in employees.values():
        total_days = sum(1 for day in employee["codes"].values() if day["code"])
        present_days = sum(
            1
            for day in employee["codes"].values()
            if day["code"] == "P" or day["code"] == "HRO"
        )
        employee["weekly_compliance"] = (
            round((present_days / total_days) * 100) if total_days else 0
        )

    # Sort employees alphabetically by first name
    sorted_employees = sorted(employees.values(), key=lambda x: x["first_name"].lower())

    context = {
        "mondays": mondays,
        "selected_week": selected_week,
        "employees": sorted_employees,  # Sorted list for template
        "point_legend": ATTENDANCE_POINTS,
    }
    return render(request, "reports/weekly_compliance_report.html", context)


@login_required
def monthly_attendance_summary(request):
    selected_month = request.GET.get("month", datetime.today().strftime("%Y-%m"))
    start_date = datetime.strptime(selected_month, "%Y-%m")
    days_in_month = monthrange(start_date.year, start_date.month)[1]
    end_date = start_date + timedelta(days=days_in_month - 1)

    restaurants = get_user_restaurants(request.user)

    records = AttendanceRecord.objects.filter(
        date__range=[start_date, end_date], employee__restaurant__in=restaurants
    )

    employees = {}

    for record in records:
        emp_id = record.employee.id
        if emp_id not in employees:
            employees[emp_id] = {
                "name": f"{record.employee.first_name} {record.employee.last_name}",
                "days_scheduled": 0,
                "days_present": 0,
                "points": 0,
            }
        employees[emp_id]["days_scheduled"] += 1
        if record.code in ["P", "HRO"]:
            employees[emp_id]["days_present"] += 1
        if record.code in ATTENDANCE_POINTS:
            employees[emp_id]["points"] += ATTENDANCE_POINTS[record.code]

    for emp in employees.values():
        emp["compliance"] = (
            round((emp["days_present"] / emp["days_scheduled"]) * 100)
            if emp["days_scheduled"]
            else 0
        )

    context = {"selected_month": selected_month, "employees": employees.values()}
    return render(request, "reports/monthly_attendance_summary.html", context)


@login_required
def monthly_attendance_detail(request):
    selected_month = request.GET.get("month", datetime.today().strftime("%Y-%m"))
    start_date = datetime.strptime(selected_month, "%Y-%m")
    days_in_month = monthrange(start_date.year, start_date.month)[1]
    end_date = start_date + timedelta(days=days_in_month - 1)

    restaurants = get_user_restaurants(request.user)

    monthly_attendance = AttendanceRecord.objects.filter(
        date__range=[start_date, end_date], employee__restaurant__in=restaurants
    )

    employees = {}

    for entry in monthly_attendance:
        if entry.employee.id not in employees:
            employees[entry.employee.id] = {
                "id": entry.employee.id,
                "name": f"{entry.employee.first_name} {entry.employee.last_name}",
                "first_name": entry.employee.first_name,
                "attendance": {
                    day: {"code": "", "comment": ""}
                    for day in range(1, days_in_month + 1)
                },
            }
        day_of_month = entry.date.day
        employees[entry.employee.id]["attendance"][day_of_month] = {
            "code": entry.code,
            "comment": entry.comment if entry.comment else "",
        }

    context = {
        "selected_month": selected_month,
        "employees": employees.values(),
        "days_in_month": range(1, days_in_month + 1),
    }
    return render(request, "reports/monthly_attendance_detail.html", context)


@login_required
def individual_attendance_report(request):
    selected_month = request.GET.get("month", datetime.today().strftime("%Y-%m"))
    start_date = datetime.strptime(selected_month, "%Y-%m")
    days_in_month = monthrange(start_date.year, start_date.month)[1]
    end_date = start_date + timedelta(days=days_in_month - 1)

    restaurants = get_user_restaurants(request.user)

    employees_with_attendance = AttendanceRecord.objects.filter(
        date__range=[start_date, end_date], employee__restaurant__in=restaurants
    )
    employee_ids = employees_with_attendance.values_list(
        "employee", flat=True
    ).distinct()
    employees = Employee.objects.filter(
        id__in=employee_ids, restaurant__in=restaurants
    ).order_by("first_name")

    employees_list = [
        {"id": emp.id, "name": f"{emp.first_name} {emp.last_name}"} for emp in employees
    ]

    selected_employee_id = request.GET.get("employee")
    if not selected_employee_id and employees_list:
        selected_employee_id = str(employees_list[0]["id"])  # Default to first employee

    selected_employee_name = None
    attendance_data = {}

    if selected_employee_id:
        try:
            selected_employee = Employee.objects.get(
                id=selected_employee_id, restaurant__in=restaurants
            )
            selected_employee_name = (
                f"{selected_employee.first_name} {selected_employee.last_name}"
            )
            attendance_records = AttendanceRecord.objects.filter(
                employee=selected_employee, date__range=[start_date, end_date]
            )

            for record in attendance_records:
                day_of_month = record.date.day
                attendance_data[day_of_month] = {
                    "code": record.code,
                    "comment": record.comment if record.comment else "",
                }
        except Employee.DoesNotExist:
            selected_employee_name = None

    context = {
        "selected_month": selected_month,
        "employees": employees_list,
        "selected_employee": selected_employee_id,
        "selected_employee_name": selected_employee_name,
        "attendance_data": attendance_data,
        "days_in_month": range(1, days_in_month + 1),
    }

    return render(request, "reports/individual_attendance_report.html", context)
