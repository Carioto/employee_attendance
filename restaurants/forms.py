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
                'class': 'block border mt-3 mb-3 border-gray-300 p-2 rounded-md w-1/4 mx-auto text-center'
            })
        
        # Force width on the select dropdown
        self.fields['restaurant'].widget.attrs.update({'style': 'width: 17%;'})


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