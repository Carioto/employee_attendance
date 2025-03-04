from datetime import date, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from .forms import AttendanceEntryForm
from .models import AttendanceRecord
from restaurants.models import Employee

import logging

logger = logging.getLogger(__name__)

@login_required
def attendance_entry(request):
    if request.user.role in ['gm', 'dm', 'superuser']:
        selected_date_str = request.GET.get('date', date.today().isoformat())
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    employees = Employee.objects.filter(restaurant=request.user.restaurant).order_by('first_name')

    initial_data = []
    for emp in employees:
        try:
            record = AttendanceRecord.objects.get(employee=emp, date=selected_date)
            initial_data.append({
                'employee_id': emp.id,
                'code': record.code,
                'comment': record.comment,
            })
        except AttendanceRecord.DoesNotExist:
            initial_data.append({
                'employee_id': emp.id,
                'code': '',
                'comment': '',
            })

    AttendanceFormSet = formset_factory(AttendanceEntryForm, extra=0)

    if request.method == 'POST':
        logger.debug("Received POST data: %s", request.POST)  # Log full POST data

        formset = AttendanceFormSet(request.POST)

        # Debugging: Check if Django recognizes any forms in the formset
        logger.debug("Total Forms in Formset: %d", formset.total_form_count())

        if formset.is_valid():
            logger.debug("Formset is valid. Processing records...")

            for index, form in enumerate(formset):
                emp_id = form.cleaned_data.get('employee_id') or request.POST.get(f'form-{index}-employee_id')
                code = form.cleaned_data.get('code')
                comment = form.cleaned_data.get('comment')

                if emp_id:
                    employee = get_object_or_404(Employee, id=emp_id)
                    logger.debug(f"Saving attendance: {employee.first_name} {employee.last_name}, Date={selected_date}, Code={code}, Comment={comment}")

                    if code != "OFF":  # Skip saving if "Not Scheduled"
                        AttendanceRecord.objects.update_or_create(
                            employee=employee,
                            date=selected_date,
                            defaults={'code': code, 'comment': comment}
                        )
                    else:
                        # Ensure we remove any existing "Not Scheduled" records
                        AttendanceRecord.objects.filter(employee=employee, date=selected_date).delete()
                        logger.debug(f"Skipped saving attendance for {employee.first_name} {employee.last_name} - Marked as OFF")


            return redirect(f"{request.path}?date={selected_date.isoformat()}")

        else:
            logger.error("Formset is NOT valid. Errors: %s", formset.errors)

    else:
        formset = AttendanceFormSet(initial=initial_data)

    form_employee = zip(formset, employees)

    context = {
        'formset': formset,
        'form_employee': form_employee,
        'selected_date': selected_date,
    }
    return render(request, 'attendance/attendance_entry.html', context)
