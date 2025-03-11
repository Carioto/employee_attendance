from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSetupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'block border mt-3 mb-3 border-gray-300 p-2 rounded-md w-1/4 mx-auto text-center'})
    )

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('user', None)  # Get the logged-in user
        super().__init__(*args, **kwargs)

        # Restrict GM to only creating 'manager' roles
        if self.request_user and self.request_user.role == 'gm':
            self.fields['role'].choices = [('manager', 'Manager')]  # Only show Manager option
            self.fields['role'].widget.attrs['disabled'] = True  # Disable dropdown to prevent selection

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'role']
        help_texts = {
            'username': None,  # Remove default Django username help text
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'block border mt-3 mb-3 border-gray-300 p-2 rounded-md w-1/4 mx-auto text-center'}),
            'first_name': forms.TextInput(attrs={'class': 'block border mt-3 mb-3 border-gray-300 p-2 rounded-md w-1/4 mx-auto text-center'}),
            'last_name': forms.TextInput(attrs={'class': 'block border mt-3 mb-3 border-gray-300 p-2 rounded-md w-1/4 mx-auto text-center'}),
            'email': forms.EmailInput(attrs={'class': 'block border mt-3 mb-3 border-gray-300 p-2 rounded-md w-1/4 mx-auto text-center'}),
            'role': forms.Select(attrs={'class': 'block border mt-3 mb-3 border-gray-300 p-2 rounded-md w-1/4 mx-auto text-center'}),
        }
