from django import forms
from .models import Employee,Restaurant

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'restaurant']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the logged-in user
        super().__init__(*args, **kwargs)
    
        # Apply CSS classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'fieldstyle w-3/4'
            })
        


        # Filter the restaurant choices based on user role
        if user:
            if user.role == 'gm':
                self.fields['restaurant'].queryset = Restaurant.objects.filter(gm=user)
            elif user.role in ['dm', 'superuser']:
                self.fields['restaurant'].queryset = Restaurant.objects.filter(district_managers=user)
            else:
                self.fields['restaurant'].queryset = Restaurant.objects.none()  # Empty for others


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'address', 'gm']