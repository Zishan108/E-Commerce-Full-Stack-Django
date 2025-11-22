from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Frontend URLs
    path('', views.home, name='home'),
    path('category/<slug:category_slug>/', views.category_products, name='category_products'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Cart URLs
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increment/<int:product_id>/', views.increment_cart, name='increment_cart'),
    path('cart/decrement/<int:product_id>/', views.decrement_cart, name='decrement_cart'),
    
    # Checkout URLs
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/place_order/', views.place_order, name='place_order'),
    
    # Order History
    path('orders/', views.order_history, name='order_history'),
]