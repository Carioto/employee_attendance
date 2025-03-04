from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Employee, Restaurant
from .forms import EmployeeForm, RestaurantForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser

class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'restaurants/employee_list.html'
    context_object_name = 'employees'

    def get_queryset(self):
        user = self.request.user
        # If the user is a GM, show employees for their restaurant.
        if user.role == 'gm' and user.restaurant:
            return Employee.objects.filter(restaurant=user.restaurant)
        # For DM and superuser, you might want to show all or a filtered list.
        elif user.role in ['dm', 'superuser']:
            return Employee.objects.all()
        return Employee.objects.none()


class EmployeeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'restaurants/employee_form.html'
    success_url = reverse_lazy('restaurants:employee_list')

    def test_func(self):
        # Only GM, DM, or superuser can add employees.
        return self.request.user.role in ['gm', 'dm', 'superuser']

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
        # GM can only update employees belonging to their restaurant.
        if user.role == 'gm' and user.restaurant:
            return employee.restaurant == user.restaurant
        # DM and superuser have broader permissions.
        return user.role in ['dm', 'superuser']


class EmployeeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Employee
    template_name = 'restaurants/employee_confirm_delete.html'
    success_url = reverse_lazy('restaurants:employee_list')

    def test_func(self):
        user = self.request.user
        employee = self.get_object()
        if user.role == 'gm' and user.restaurant:
            return employee.restaurant == user.restaurant
        return user.role in ['dm', 'superuser']


class RestaurantListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Restaurant
    template_name = 'restaurants/restaurant_list.html'
    context_object_name = 'restaurants'

    def test_func(self):
        # Allow only superusers and DMs to manage restaurants
        return self.request.user.role in ['superuser', 'dm']

class RestaurantUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'restaurants/restaurant_form.html'
    success_url = reverse_lazy('restaurants:restaurant_list')

    def test_func(self):
        return self.request.user.role in ['superuser', 'dm']


@login_required
def restaurant_list(request):
    restaurants = Restaurant.objects.all().order_by('name')
    gms = CustomUser.objects.filter(role='gm').order_by('first_name')
    return render(request, 'restaurants/restaurant_list.html', {'restaurants': restaurants, 'gms': gms})

@login_required
def assign_gm(request):
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


