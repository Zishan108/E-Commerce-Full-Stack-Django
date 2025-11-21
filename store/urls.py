from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Product / Category Pages
    path('', views.home, name='home'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    # Cart Pages
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increment/<int:product_id>/', views.increment_cart, name='increment_cart'),
    path('cart/decrement/<int:product_id>/', views.decrement_cart, name='decrement_cart'),
    path('checkout/', views.checkout, name='checkout'),

]
