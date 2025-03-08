from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from attendance.models import AttendanceRecord
from restaurants.models import Employee

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
    three_months_ago = start_date - timedelta(days=90)
    
    # Fetch attendance records for the selected week
    weekly_attendance = AttendanceRecord.objects.filter(date__range=[start_date, end_date])
    # Fetch attendance records for the past 3 months
    three_months_attendance = AttendanceRecord.objects.filter(date__range=[three_months_ago, end_date])
    
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
    for entry in three_months_attendance:
        if entry.employee.id in employees and entry.code in ATTENDANCE_POINTS:
            employees[entry.employee.id]['point_total'] += ATTENDANCE_POINTS[entry.code]
    
    # Calculate weekly compliance percentage
    for employee in employees.values():
        total_days = sum(1 for day in employee['codes'].values() if day['code'])
        present_days = sum(1 for day in employee['codes'].values() if day['code'] == 'P' or day['code'] == 'HRO')
        employee['weekly_compliance'] = round((present_days / total_days) * 100, 2) if total_days else 0
    
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
    end_date = start_date + timedelta(days=31)
    
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
            employee['percent_compliant'] = round((employee['total_present'] / employee['total_scheduled']) * 100, 2)
        
    sorted_employees = sorted(employees.values(), key=lambda x: x['first_name'].lower())
    
    context = {
        'selected_month': selected_month,
        'employees': sorted_employees,
    }
    return render(request, 'reports/monthly_attendance_summary.html', context)
