from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('setup/', views.user_setup, name='user_setup'),
]