from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("setup/", views.user_setup, name="user_setup"),
    path("manage-users/", views.manage_users, name="manage_users"),
    path("edit-user/<int:user_id>", views.edit_user, name="edit_user"),
    path("reset-password/<int:user_id>", views.reset_password, name="reset_password"),
    path("delete-user/<int:user_id>", views.delete_user, name="delete_user"),
]
