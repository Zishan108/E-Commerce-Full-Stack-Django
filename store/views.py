from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Category, Product, CartItem, Order, OrderItem
from django.db.models import Q, Sum, Count
from decimal import Decimal
import random
import string

def home(request):
    """Home page view"""
    categories = Category.objects.all()
    
    # Get trending products (top 10 most sold products)
    trending_products = Product.objects.filter(
        is_active=True,
        orderitem__isnull=False
    ).annotate(
        total_sold=Sum('orderitem__quantity')
    ).order_by('-total_sold')[:10]
    
    # If not enough sold products, supplement with featured products
    if trending_products.count() < 10:
        featured_products = Product.objects.filter(
            is_active=True
        ).exclude(
            id__in=[p.id for p in trending_products]
        ).order_by('-created_at')[:10-trending_products.count()]
        trending_products = list(trending_products) + list(featured_products)
    
    # Get latest products (newest arrivals)
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:12]
    
    # Get featured products for other sections if needed
    featured_products = Product.objects.filter(is_active=True).order_by('?')[:8]  # Random 8 products
    
    # Get cart count for authenticated users
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    
    context = {
        'categories': categories,
        'trending_products': trending_products,  # For trendy section
        'latest_products': latest_products,      # For latest products section
        'featured_products': featured_products,  # For featured section if needed
        'cart_count': cart_count,
    }
    return render(request, 'store/home.html', context)

def category_products(request, category_slug):
    """View to display products by category"""
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, is_active=True)
    
    # Get cart count for authenticated users
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    
    context = {
        'category': category,
        'products': products,
        'categories': Category.objects.all(),
        'cart_count': cart_count,
    }
    return render(request, 'store/category_products.html', context)

def product_detail(request, slug):
    """Product detail view"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    context = {
        'product': product,
    }
    return render(request, 'store/product_detail.html', context)

@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # AJAX request
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Product is out of stock!',
                })
        
        cart_count = CartItem.objects.filter(user=request.user).count()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Product added to cart!',
            'cart_count': cart_count
        })
    
    # Non-AJAX request (fallback)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created and cart_item.quantity < product.stock:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('store:cart_view')

@login_required
def cart_view(request):
    """Display cart items"""
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    
    context = {
        'items': cart_items,
        'total': total,
    }
    return render(request, 'store/cart.html', context)

@login_required
def remove_from_cart(request, product_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
    cart_item.delete()
    return redirect('store:cart_view')

@login_required
def increment_cart(request, product_id):
    """Increase item quantity in cart"""
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
    if cart_item.quantity < cart_item.product.stock:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('store:cart_view')

@login_required
def decrement_cart(request, product_id):
    """Decrease item quantity in cart"""
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('store:cart_view')

@login_required
def checkout(request):
    """Checkout page"""
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    
    context = {
        'items': cart_items,
        'total': total,
    }
    return render(request, 'store/checkout.html', context)

@login_required
def place_order(request):
    """Place order and create order record"""
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items.exists():
            return redirect('store:cart_view')
        
        # Generate unique order ID
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            order_id=order_id,
            is_paid=True  # Assuming payment is successful for demo
        )
        
        # Create order items and update stock
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            
            # Update product stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
        
        # Clear cart
        cart_items.delete()
        
        return redirect('store:order_history')
    
    return redirect('store:checkout')

@login_required
def order_history(request):
    """Display user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'store/order_history.html', context)