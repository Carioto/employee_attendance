from django.shortcuts import render, get_object_or_404 ,redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import UserSetupForm
from .forms import UserEditForm, PasswordResetForm

User = get_user_model()

@login_required
def user_setup(request):
    if request.user.role not in ['superuser', 'dm', 'gm']:
        raise PermissionDenied

    if request.method == 'POST':
        form = UserSetupForm(request.POST, user=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            new_user_role = form.cleaned_data['role']

            # Restrict GM to only creating manager accounts
            if request.user.role == 'gm':
                if user.role != 'manager':
                    messages.error(request, "You can only create manager accounts.")
                    return render(request, 'accounts/user_setup.html', {'form': form})

                if request.user.restaurant:
                    user.restaurant = request.user.restaurant
                else:
                    messages.error(request, "You must have an assigned restaurant to create a manager.")
                    return render(request, 'accounts/user_setup.html', {'form': form})

            # Superuser & DM can assign any restaurant
            elif request.user.role == 'superuser':
                if new_user_role == 'gm' or new_user_role == 'manager':
                    user.restaurant = form.cleaned_data['restaurant']
                elif new_user_role == 'dm':
                    selected_restaurants = form.cleaned_data.get('restaurants')
                    if selected_restaurants:
                        user.restaurants.set(selected_restaurants)
            elif request.user.role == 'dm':
                user.restaurant = form.cleaned_data['restaurant']
                
            try:
                user.save()
                messages.success(request, f"User {user.username} created successfully!")
            except Exception as e:
                print("Error saving user:", e)
                messages.error(request, "There was an error creating the user.")
                return render(request, 'accounts/user_setup.html', {'form': form})
            return redirect('accounts:user_setup')

        else:
            print("Form errors:", form.errors)  # Debugging errors

    else:
        form = UserSetupForm(user=request.user)

    return render(request, 'accounts/user_setup.html', {'form': form})

@login_required
def manage_users(request):
    user = request.user

    # Superusers can see all users
    if user.role == 'superuser':
        users = User.objects.all()
    # DMs can see users in their assigned restaurants
    elif user.role == 'dm':
        users = User.objects.filter(restaurant__in=user.restaurants.all())  # Assuming DM has multiple restaurants
    # GMs can see only their restaurant users
    elif user.role == 'gm':
         # Block GMs with no assigned restaurant
        if user.restaurant == None:
            messages.error(request, "You must be assigned to a restaurant to manage users.")
            return redirect('accounts:user_setup')  # or redirect to a safe page
        users = User.objects.filter(restaurant=user.restaurant)
    else:
        raise PermissionDenied  # Other users cannot access this page
    context = {
        'gm':user,
        'users':users
    }

    return render(request, 'accounts/manage_users.html', context)

@login_required
def edit_user(request, user_id):
    user = request.user
    target_user = get_object_or_404(User, id=user_id)

    # Restrict based on role
    if user.role not in ['superuser', 'dm', 'gm']:
        raise PermissionDenied
    if user.role == 'gm' and target_user.restaurant != user.restaurant:
        raise PermissionDenied  # GM can only edit their restaurant's users
    if user.role == 'dm' and target_user.restaurant not in user.restaurants.all():
        raise PermissionDenied  # DM can only edit their assigned restaurants

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=target_user, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"{target_user.username}'s details updated.")
            return redirect('accounts:manage_users')
    else:
        form = UserEditForm(instance=target_user, user=user)

    return render(request, 'accounts/edit_user.html', {'form': form, 'target_user': target_user})

@login_required
def reset_password(request, user_id):
    user = request.user
    target_user = get_object_or_404(User, id=user_id)

    # Restrict based on role
    if user.role not in ['superuser', 'dm', 'gm']:
        raise PermissionDenied
    if user.role == 'gm' and target_user.restaurant != user.restaurant:
        raise PermissionDenied
    if user.role == 'dm' and target_user.restaurant not in user.restaurants.all():
        raise PermissionDenied

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            target_user.set_password(new_password)
            target_user.save()
            messages.success(request, f"Password for {target_user.username} has been reset.")
            return redirect('accounts:manage_users')
    else:
        form = PasswordResetForm()

    return render(request, 'accounts/reset_password.html', {'form': form, 'target_user': target_user})

@login_required
def delete_user(request, user_id):
    user = request.user
    target_user = get_object_or_404(User, id=user_id)

    if user.role == 'superuser':
       pass
    # GM: can only delete managers in their restaurant
    elif user.role == 'gm':
       if target_user.restaurant != user.restaurant:
           raise PermissionDenied

    if request.method == 'POST':
        target_user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('accounts:manage_users')

    return render(request, 'accounts/delete_user.html', {'target_user': target_user})



def custom_404_view(request, exception):
    return render(request, "404.html", status=404)