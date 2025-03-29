from django import forms
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant  # Import Restaurant model

User = get_user_model()

class UserSetupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'block border mt-3 mb-3 border-gray-300 p-2 rounded-md w-1/4 mx-auto text-center'})
    )
    restaurant = forms.ModelChoiceField(
        queryset=Restaurant.objects.all(),
        required=False,  # Allow None for superusers/DMs, but GMs will get auto-assigned
        widget=forms.Select(attrs={'class': 'fieldstyle w-3/4'})
    )
    restaurants = forms.ModelMultipleChoiceField(
        queryset=Restaurant.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'fieldstyle w-3/4', 'id': 'id_restaurants'})
    )


    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('user', None)  # Get the logged-in user
        super().__init__(*args, **kwargs)

        if self.request_user and self.request_user.role == 'gm':
            self.fields['role'].choices = [('manager', 'Manager')]  # GM can only create managers
            self.fields['role'].widget.attrs['readonly'] = True  # Make it readonly instead of disabled
            self.fields['restaurants'].widget = forms.HiddenInput()

            # Ensure the GM's restaurant is selected and readonly
            if self.request_user.restaurant:
                self.fields['restaurant'].queryset = Restaurant.objects.filter(id=self.request_user.restaurant.id)
                self.fields['restaurant'].initial = self.request_user.restaurant
                self.fields['restaurant'].widget.attrs['readonly'] = True  # Read-only, not disabled
            else:
                self.fields['restaurant'].queryset = Restaurant.objects.none()
                self.fields['restaurant'].help_text = "You must have an assigned restaurant to create a manager."
        elif self.request_user and self.request_user.role == 'dm':
                # Limit both fields to only show the DM's assigned restaurants
                allowed = self.request_user.restaurants.all()
                self.fields['restaurant'].queryset = allowed
                self.fields['restaurants'].queryset = allowed
                 # ✅ Only allow DM to create GM or Manager
                self.fields['role'].choices = [
                    ('gm', 'General Manager'),
                    ('manager', 'Manager'),
                ]


    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'role', 'restaurant','restaurants']
        help_texts = {
            'username': None,
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'fieldstyle'}),
            'first_name': forms.TextInput(attrs={'class': 'fieldstyle'}),
            'last_name': forms.TextInput(attrs={'class': 'fieldstyle'}),
            'email': forms.EmailInput(attrs={'class': 'fieldstyle'}),
            'role': forms.Select(attrs={'class': 'fieldstyle w-3/4'}),
            'restaurant': forms.Select(attrs={'class': 'fieldstyle'}),
        }

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'restaurant']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'fieldstyle'}),
            'last_name': forms.TextInput(attrs={'class': 'fieldstyle'}),
            'email': forms.EmailInput(attrs={'class': 'fieldstyle'}),
            'role': forms.Select(attrs={'class': 'fieldstyle'}),
            'restaurant': forms.Select(attrs={'class': 'fieldstyle'}),
        }

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('user', None)  # Get logged-in user
        super().__init__(*args, **kwargs)

        # Only superusers can change role
        if self.request_user.role != 'superuser':
            self.fields.pop('role')  # Remove role field for non-superusers

        # GMs cannot change restaurant, auto-assign to their restaurant
        if self.request_user.role == 'gm':
            self.fields['restaurant'].queryset = Restaurant.objects.filter(id=self.request_user.restaurant.id)
            self.fields['restaurant'].initial = self.request_user.restaurant
            self.fields['restaurant'].widget.attrs['readonly'] = True

class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'block text-center mx-auto'}))