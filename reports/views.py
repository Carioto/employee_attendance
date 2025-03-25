from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from attendance.models import AttendanceRecord
from restaurants.models import Employee
from calendar import monthrange

def get_mondays():
    """ Generate a list of Monday dates for the dropdown."""
    today = datetime.today()
    mondays = [(today - timedelta(days=today.weekday()) - timedelta(weeks=i)).strftime('%Y-%m-%d') for i in range(10)]
    return sorted(mondays, reverse=True)

# Point values for attendance violations
ATTENDANCE_POINTS = {
    'NS': 3,   # No call no show
    'LCO': 2,  # Calling Off Without Notice
    'CO': 1,   # Calling Off with Notice
    'L': 0.5,  # Late (>10 minutes)
    'XL': 1,   # Excessively Late (>30 minutes)
    'P': 0,    # Present
    'HRO': -1  # Hero (extra shift incentive)
}

@login_required
def reports_home(request):
    return render(request, 'reports/reports_home.html')

@login_required
def weekly_compliance_report(request):
    mondays = get_mondays()
    selected_week = request.GET.get('week', mondays[0])  # Default to most recent Monday
    start_date = datetime.strptime(selected_week, '%Y-%m-%d')
    end_date = start_date + timedelta(days=6)
    two_months_ago = start_date - timedelta(days=60)
    
    # Fetch attendance records for the selected week
    weekly_attendance = AttendanceRecord.objects.filter(date__range=[start_date, end_date])
    # Fetch attendance records for the past 3 months
    two_months_attendance = AttendanceRecord.objects.filter(date__range=[two_months_ago, end_date])
    
    employees = {}
    
    for entry in weekly_attendance:
        if entry.employee.id not in employees:
            employees[entry.employee.id] = {
                'name': f"{entry.employee.first_name} {entry.employee.last_name}",
                'first_name': entry.employee.first_name,  # Store first name for sorting
                'codes': {day: {'code': '', 'color': '', 'comment': ''} for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']},
                'point_total': 0,  # Initialize point total
                'weekly_compliance': 0  # Initialize weekly compliance percentage
            }
        
        weekday = entry.date.strftime('%A').lower()  # Get weekday name in lowercase
        employees[entry.employee.id]['codes'][weekday] = {
            'code': entry.code,  # The attendance code
            'color': '',  # Placeholder for color logic (to be added later)
            'comment': entry.comment if entry.comment else ''  # Pass the comment to the template
        }
    
    # Calculate 3-month point total
    for entry in two_months_attendance:
        if entry.employee.id in employees and entry.code in ATTENDANCE_POINTS:
            employees[entry.employee.id]['point_total'] += ATTENDANCE_POINTS[entry.code]
    
    # Calculate weekly compliance percentage
    for employee in employees.values():
        total_days = sum(1 for day in employee['codes'].values() if day['code'])
        present_days = sum(1 for day in employee['codes'].values() if day['code'] == 'P' or day['code'] == 'HRO')
        employee['weekly_compliance'] = round((present_days / total_days) * 100) if total_days else 0
    
    # Sort employees alphabetically by first name
    sorted_employees = sorted(employees.values(), key=lambda x: x['first_name'].lower())
    
    context = {
        'mondays': mondays,
        'selected_week': selected_week,
        'employees': sorted_employees,  # Sorted list for template
        'point_legend': ATTENDANCE_POINTS
    }
    return render(request, 'reports/weekly_compliance_report.html', context)

@login_required
def monthly_attendance_summary(request):
    selected_month = request.GET.get('month', datetime.today().strftime('%Y-%m'))
    start_date = datetime.strptime(selected_month, '%Y-%m')
    days_in_month = monthrange(start_date.year, start_date.month)[1]  # Get the correct number of days in the month
    end_date = start_date + timedelta(days=days_in_month - 1)
    
    monthly_attendance = AttendanceRecord.objects.filter(date__range=[start_date, end_date])
    employees = {}
    
    for entry in monthly_attendance:
        if entry.employee.id not in employees:
            employees[entry.employee.id] = {
                'name': f"{entry.employee.first_name} {entry.employee.last_name}",
                'first_name': entry.employee.first_name,
                'total_scheduled': 0,
                'total_present': 0,
                'total_absent': 0,
                'total_late': 0,
                'percent_compliant': 0,
            }
        
        employees[entry.employee.id]['total_scheduled'] += 1
        
        if entry.code == 'P' or entry.code == 'HRO':
            employees[entry.employee.id]['total_present'] += 1
        elif entry.code in ['NS', 'LCO', 'CO']:
            employees[entry.employee.id]['total_absent'] += 1
        elif entry.code in ['L', 'XL']:
            employees[entry.employee.id]['total_late'] += 1
        
    for employee in employees.values():
        if employee['total_scheduled'] > 0:
            employee['percent_compliant'] = round((employee['total_present'] / employee['total_scheduled']) * 100)
        
    sorted_employees = sorted(employees.values(), key=lambda x: x['first_name'].lower())
    
    context = {
        'selected_month': selected_month,
        'employees': sorted_employees,
    }
    return render(request, 'reports/monthly_attendance_summary.html', context)

@login_required
def monthly_attendance_detail(request):
    try:
        selected_month = request.GET.get('month', datetime.today().strftime('%Y-%m'))
        start_date = datetime.strptime(selected_month, '%Y-%m')
    except ValueError:
        selected_month = datetime.today().strftime('%Y-%m')
        start_date = datetime.strptime(selected_month, '%Y-%m')
    
    days_in_month = monthrange(start_date.year, start_date.month)[1]  # Get correct number of days
    end_date = start_date + timedelta(days=days_in_month - 1)
    
    monthly_attendance = AttendanceRecord.objects.filter(date__range=[start_date, end_date])
    employees = {}
    
    for entry in monthly_attendance:
        if entry.employee.id not in employees:
            employees[entry.employee.id] = {
                 'id': entry.employee.id,  # Ensure ID is included
                'name': f"{entry.employee.first_name} {entry.employee.last_name}",
                'first_name': entry.employee.first_name,
                'attendance': {day: {'code': '', 'comment': ''} for day in range(1, days_in_month + 1)}
            }
        
        day_of_month = entry.date.day
        if day_of_month in employees[entry.employee.id]['attendance']:
            employees[entry.employee.id]['attendance'][day_of_month] = {
                'code': entry.code,
                'comment': entry.comment if entry.comment else ''
            }
    
    sorted_employees = sorted(employees.values(), key=lambda x: x['first_name'].lower())
    
    context = {
        'selected_month': selected_month,
        'employees': sorted_employees,
        'days_in_month': range(1, days_in_month + 1)  # Ensure it's iterable in template
    }
    
    if not employees:
        context['employees'] = []  # Prevent template from breaking due to empty data
    
    return render(request, 'reports/monthly_attendance_detail.html', context)

@login_required
def individual_attendance_report(request):
    selected_month = request.GET.get('month', datetime.today().strftime('%Y-%m'))
    start_date = datetime.strptime(selected_month, '%Y-%m')
    days_in_month = monthrange(start_date.year, start_date.month)[1]
    end_date = start_date + timedelta(days=days_in_month - 1)

    # Get employees with attendance records in the selected month
    employees_with_attendance = AttendanceRecord.objects.filter(date__range=[start_date, end_date])
    employee_ids = employees_with_attendance.values_list('employee', flat=True).distinct()
    employees = Employee.objects.filter(id__in=employee_ids).order_by('first_name')

    # Convert employees to a list with names for the dropdown
    employees_list = [{'id': emp.id, 'name': f"{emp.first_name} {emp.last_name}"} for emp in employees]

    # Get selected employee ID from the request or default to the first available employee
    selected_employee_id = request.GET.get('employee')
    print(selected_employee_id)
    if not selected_employee_id:
        selected_employee_name = None
    attendance_data = {}

    if selected_employee_id:
        try:
            selected_employee = Employee.objects.get(id=selected_employee_id)
            selected_employee_name = f"{selected_employee.first_name} {selected_employee.last_name}"
            attendance_records = AttendanceRecord.objects.filter(employee=selected_employee, date__range=[start_date, end_date])

            for record in attendance_records:
                day_of_month = record.date.day
                attendance_data[day_of_month] = {
                    'code': record.code,
                    'comment': record.comment if record.comment else ''
                }
        except Employee.DoesNotExist:
            selected_employee_name = None

    context = {
        'selected_month': selected_month,
        'employees': employees_list,
        'selected_employee': selected_employee_id,
        'selected_employee_name': selected_employee_name,  # Now passed to the template
        'attendance_data': attendance_data,
        'days_in_month': range(1, days_in_month + 1),
    }

    return render(request, 'reports/individual_attendance_report.html', context)