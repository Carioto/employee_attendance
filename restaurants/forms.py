from django import forms
from .models import Employee, Restaurant
from accounts.models import CustomUser


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ["first_name", "last_name", "restaurant"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # Get the logged-in user
        super().__init__(*args, **kwargs)

        # Apply CSS classes
        for field in self.fields:
            self.fields[field].widget.attrs.update(
                {"class": "fieldstyle w-3/4 sm:w-1/2"}
            )

        # Filter the restaurant choices based on user role
        if user:
            if user.role == "gm":
                self.fields["restaurant"].queryset = Restaurant.objects.filter(
                    gm=user
                ).order_by("name")
            elif user.role == "superuser":
                self.fields["restaurant"].queryset = Restaurant.objects.all().order_by(
                    "name"
                )
            elif user.role == "dm":
                self.fields["restaurant"].queryset = user.restaurants.all().order_by(
                    "name"
                )
            else:
                self.fields["restaurant"].queryset = (
                    Restaurant.objects.none()
                )  # Empty for others


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ["name", "address", "gm"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["gm"].queryset = CustomUser.objects.filter(role="gm")
        # Optional: add styling
        self.fields["gm"].widget.attrs.update({"class": "fieldstyle w-3/4"})
