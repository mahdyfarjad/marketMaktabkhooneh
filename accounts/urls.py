from django.urls import path
from . import views

urlpatterns = [
    path('customer/register/', views.registerCustomer),
    path('customer/list/', views.customerList),
    path('customer/<int:id>/', views.customerInfo),
    path('customer/<int:id>/edit/', views.customerEdit),
    path('customer/login/', views.login),
    path('customer/logout/', views.logout),
    path('customer/profile/', views.profile),
]