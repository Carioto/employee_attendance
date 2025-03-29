from django.urls import path
from .views import (
    EmployeeListView,
    EmployeeCreateView,
    EmployeeUpdateView,
    EmployeeDeleteView,
    RestaurantListView,
    RestaurantUpdateView,
    assign_gm,
)

app_name = 'restaurants'

urlpatterns = [
    path('employees/', EmployeeListView.as_view(), name='employee_list'),
    path('employees/new/', EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/edit/', EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/delete/', EmployeeDeleteView.as_view(), name='employee_delete'),
    path('<int:pk>/edit/', RestaurantUpdateView.as_view(), name='restaurant_update'),
    path('restaurants/', RestaurantListView.as_view(), name='restaurant_list'),
    path('assign-gm/', assign_gm, name='assign_gm'),
]
