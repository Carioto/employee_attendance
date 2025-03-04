from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from two_factor.views import LoginView
from django.conf.urls import handler404
from accounts.views import custom_404_view  # Import the 404 view

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('welcome/', TemplateView.as_view(template_name='welcome.html'), name='welcome'),
    path('admin/', admin.site.urls),

    # App URLs with namespaces
    path('attendance/', include('attendance.urls', namespace='attendance')),
    path('restaurants/', include('restaurants.urls', namespace='restaurants')),
    path('reports/', include('reports.urls', namespace='reports')),

    # ✅ Fix: Explicitly define app_name before including two_factor.urls
    path('account/', include('two_factor.urls', namespace='two_factor')),

]

handler404 = custom_404_view