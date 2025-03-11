from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from django.conf.urls import handler404
from accounts.views import custom_404_view  # Import the 404 view
from django.conf.urls import handler403
from restaurants.views import custom_permission_denied_view

urlpatterns = [
    path('', lambda request: redirect('login', permanent=False)),  # ✅ Redirect / to /login/
    path('login/', LoginView.as_view(template_name="registration/login.html"), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('welcome/', TemplateView.as_view(template_name='welcome.html'), name='welcome'),
    path('admin/', admin.site.urls),

    # App URLs with namespaces
    path('attendance/', include(('attendance.urls', 'attendance'), namespace='attendance')),
    path('restaurants/', include(('restaurants.urls', 'restaurants'), namespace='restaurants')),
    path('reports/', include(('reports.urls', 'reports'), namespace='reports')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
]

handler404 = custom_404_view
handler403 = custom_permission_denied_view