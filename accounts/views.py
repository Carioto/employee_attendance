from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import UserSetupForm

User = get_user_model()

@login_required
def user_setup(request):
    # Restrict access to superusers and DMs
    if request.user.role not in ['superuser', 'dm', 'gm']:
        raise PermissionDenied  # GMs will be added later

    if request.method == 'POST':
        form = UserSetupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash password
            user.first_name = form.cleaned_data['first_name']  # Save first name
            user.last_name = form.cleaned_data['last_name']  # Save last name
            # Restrict GM to only creating manager accounts
            if request.user.role == 'gm' and user.role != 'manager':
                messages.error(request, "You can only create manager accounts.")
                return render(request, 'accounts/user_setup.html', {'form': form})  # Re-render form with error message

            user.save()
            messages.success(request, f"User {user.username} created successfully!")
            return redirect('accounts:user_setup')  # Redirect after success
    else:
        form = UserSetupForm()

    return render(request, 'accounts/user_setup.html', {'form': form})


def custom_404_view(request, exception):
    return render(request, "404.html", status=404)