from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from .models import Employee, Restaurant
from .forms import EmployeeForm, RestaurantForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser

def custom_permission_denied_view(request, exception=None):
    return render(request, "errors/403.html", status=403)

class EmployeeListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Employee
    template_name = 'restaurants/employee_list.html'
    context_object_name = 'employees'

    def test_func(self):
        if self.request.user.role not in ['gm', 'dm', 'superuser']:
            raise PermissionDenied  # Explicitly deny unauthorized access
        return True

    def get_queryset(self):
        user = self.request.user
        if user.role == 'gm' and user.restaurant:
            return Employee.objects.filter(restaurant=user.restaurant).order_by('first_name')
        elif user.role in ['dm', 'superuser']:
            return Employee.objects.all().order_by('first_name')
        return Employee.objects.none()

class EmployeeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'restaurants/employee_form.html'
    success_url = reverse_lazy('restaurants:employee_list')

    def test_func(self):
        if self.request.user.role not in ['gm', 'dm', 'superuser']:
            raise PermissionDenied  # Explicitly deny unauthorized access
        return True

    def form_valid(self, form):
        user = self.request.user
        # If a GM is creating an employee, automatically assign the restaurant.
        if user.role == 'gm' and user.restaurant:
            form.instance.restaurant = user.restaurant
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the logged-in user
        return kwargs


class EmployeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'restaurants/employee_form.html'
    success_url = reverse_lazy('restaurants:employee_list')

    def test_func(self):
        user = self.request.user
        employee = self.get_object()

        if user.role == 'gm' and user.restaurant:
            if employee.restaurant != user.restaurant:
                raise PermissionDenied  # GM can only edit employees from their restaurant
        elif user.role not in ['dm', 'superuser']:
            raise PermissionDenied  # Only GM, DM, or Superuser can edit

        return True


class EmployeeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Employee
    template_name = 'restaurants/employee_confirm_delete.html'
    success_url = reverse_lazy('restaurants:employee_list')

    def test_func(self):
        user = self.request.user
        employee = self.get_object()

        if user.role == 'gm' and user.restaurant:
            if employee.restaurant != user.restaurant:
                raise PermissionDenied  # GM can only delete employees from their restaurant
        elif user.role not in ['dm', 'superuser']:
            raise PermissionDenied  # Only GM, DM, or Superuser can delete

        return True

class RestaurantListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Restaurant
    template_name = 'restaurants/restaurant_list.html'
    context_object_name = 'restaurants'

    def test_func(self):
        if self.request.user.role not in ['superuser', 'dm']:
            raise PermissionDenied  # This explicitly denies access instead of just returning False
        return True

class RestaurantUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'restaurants/restaurant_form.html'
    success_url = reverse_lazy('restaurants:restaurant_list')

    def test_func(self):
        if self.request.user.role not in ['superuser', 'dm']:
            raise PermissionDenied  # This explicitly denies access instead of just returning False
        return True

@login_required
def restaurant_list(request):
    if request.user.role not in ['superuser', 'dm']:
        raise PermissionDenied  # Restrict access to unauthorized users
    restaurants = Restaurant.objects.all().order_by('name')
    gms = CustomUser.objects.filter(role='gm').order_by('first_name')
    return render(request, 'restaurants/restaurant_list.html', {'restaurants': restaurants, 'gms': gms})

@login_required
def assign_gm(request):
    if request.user.role not in ['superuser', 'dm']:
        raise PermissionDenied  # Prevent unauthorized access

    if request.method == 'POST':
        restaurant_id = request.POST.get('restaurant_id')
        gm_id = request.POST.get('gm_id')  # This can be an empty string if "None" is selected

        restaurant = get_object_or_404(Restaurant, id=restaurant_id)

        # Remove GM assignment from the previous GM (if any)
        if restaurant.gm:
            previous_gm = restaurant.gm
            previous_gm.restaurant = None
            previous_gm.save()

        if gm_id:  # If a GM is selected, assign them
            gm = get_object_or_404(CustomUser, id=gm_id, role='gm')
            restaurant.gm = gm
            gm.restaurant = restaurant  # Update GM's restaurant field
            gm.save()  # Save the updated GM data
        else:  # If "None" is selected, remove GM assignment
            restaurant.gm = None

        restaurant.save()

    return redirect('restaurants:restaurant_list')


