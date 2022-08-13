from django.urls import path
from . import views

urlpatterns = [
    path('product/insert/', views.insertProduct, name='insertProduct'),
    path('product/list/', views.productList, name='productList'),
    path('product/<int:id>/', views.prodcutInfo, name='productInfo'),
]