from django.urls import path
from . import views

urlpatterns = [
    path('product/insert/', views.insertProduct, name='insertProduct'),
    path('product/list/', views.productList, name='productList'),
    path('product/<int:id>/', views.prodcutInfo, name='productInfo'),
    path('shopping/cart/', views.shoppingCart, name='shoppingcart'),
    path('shopping/cart/add_items/', views.addItem, name='addItem'),
    path('shopping/cart/remove_items/', views.removeItem, name='addItem'),
    path('shopping/submit/', views.submit, name='submit'),
]