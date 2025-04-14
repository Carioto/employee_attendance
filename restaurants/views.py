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
    template_name = "restaurants/employee_list.html"
    context_object_name = "employees"

    def test_func(self):
        if self.request.user.role not in ["gm", "dm", "superuser"]:
            raise PermissionDenied  # Explicitly deny unauthorized access
        return True

    def get_queryset(self):
        user = self.request.user
        if user.role == "gm" and user.restaurant:
            return Employee.objects.filter(restaurant=user.restaurant).order_by(
                "first_name"
            )
        elif user.role == "dm":
            return Employee.objects.filter(
                restaurant__in=user.restaurants.all()
            ).order_by("first_name")
        elif user.role == "superuser":
            return Employee.objects.all().order_by("first_name")
        return Employee.objects.none()


class EmployeeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "restaurants/employee_form.html"
    success_url = reverse_lazy("restaurants:employee_list")

    def test_func(self):
        if self.request.user.role not in ["gm", "dm", "superuser"]:
            raise PermissionDenied  # Explicitly deny unauthorized access
        return True

    def form_valid(self, form):
        user = self.request.user
        # If a GM is creating an employee, automatically assign the restaurant.
        if user.role == "gm" and user.restaurant:
            form.instance.restaurant = user.restaurant
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # Pass the logged-in user
        return kwargs


class EmployeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "restaurants/employee_form.html"
    success_url = reverse_lazy("restaurants:employee_list")

    def test_func(self):
        user = self.request.user
        employee = self.get_object()

        if user.role == "gm" and user.restaurant:
            if employee.restaurant != user.restaurant:
                raise PermissionDenied
        elif user.role not in ["dm", "superuser"]:
            raise PermissionDenied  # Only GM, DM, or Superuser can edit

        return True


class EmployeeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Employee
    template_name = "restaurants/employee_confirm_delete.html"
    success_url = reverse_lazy("restaurants:employee_list")

    def test_func(self):
        user = self.request.user
        employee = self.get_object()

        if user.role == "gm" and user.restaurant:
            if employee.restaurant != user.restaurant:
                raise PermissionDenied
        elif user.role not in ["dm", "superuser"]:
            raise PermissionDenied  # Only GM, DM, or Superuser can delete

        return True


class RestaurantListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Restaurant
    template_name = "restaurants/restaurant_list.html"
    context_object_name = "restaurants"

    def test_func(self):
        if self.request.user.role not in ["superuser", "dm"]:
            raise PermissionDenied
        return True

    def get_queryset(self):
        user = self.request.user
        if user.role == "superuser":
            return Restaurant.objects.all().order_by("name")
        elif user.role == "dm":
            return user.restaurants.all().order_by(
                "name"
            )  # ✅ DMs only see their assigned restaurants
        return Restaurant.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["gms"] = CustomUser.objects.filter(role="gm").order_by(
            "first_name"
        )  # ✅ GMs for modal
        return context


class RestaurantUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = "restaurants/restaurant_form.html"
    success_url = reverse_lazy("restaurants:restaurant_list")

    def test_func(self):
        if self.request.user.role not in ["superuser", "dm"]:
            raise PermissionDenied
        return True


@login_required
def assign_gm(request):
    if request.user.role not in ["superuser", "dm"]:
        raise PermissionDenied

    if request.method == "POST":
        restaurant_id = request.POST.get("restaurant_id")
        gm_id = request.POST.get("gm_id")

        restaurant = get_object_or_404(Restaurant, id=restaurant_id)

        # Unassign GM from this restaurant
        if not gm_id:
            if restaurant.gm:
                restaurant.gm.restaurant = (
                    None  # Clear GM's reference to this restaurant
                )
                restaurant.gm.save()
            restaurant.gm = None
            restaurant.save()
            return redirect("restaurants:restaurant_list")

        # Assign new GM
        new_gm = get_object_or_404(CustomUser, id=gm_id, role="gm")

        # Remove GM from any other restaurant
        existing_restaurant = (
            Restaurant.objects.filter(gm=new_gm).exclude(id=restaurant.id).first()
        )
        if existing_restaurant:
            existing_restaurant.gm = None
            existing_restaurant.save()

        # Update the GM's user record
        new_gm.restaurant = restaurant
        new_gm.save()

        # Assign to this restaurant
        restaurant.gm = new_gm
        restaurant.save()

    return redirect("restaurants:restaurant_list")
