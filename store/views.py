from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from .models import Category, Product, CartItem, Order, OrderItem

# -----------------------
# Product / Category Views
# -----------------------
def home(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True)[:8]

    cart_count = 0
    recent_orders = []
    if request.user.is_authenticated:
        cart_count = request.user.cart_items.count()
        recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]

    return render(request, 'store/home.html', {
        'categories': categories,
        'products': products,
        'cart_count': cart_count,
        'recent_orders': recent_orders
    })

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_active=True)
    return render(request, 'store/category_products.html', {'category': category, 'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/product_detail.html', {'product': product})

# -----------------------
# Cart Views
# -----------------------
def add_to_cart(request, product_id):
    # Check if user is logged in
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'You must log in first!'}, status=403)
        else:
            return redirect('users:login')

    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': f'{product.name} added to cart!'})
    else:
        messages.success(request, f"Added {product.name} to cart.")
        return redirect('store:cart_view')

def cart_view(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must log in to view your cart.")
        return redirect('users:login')

    items = request.user.cart_items.all()
    total = sum(item.total_price() for item in items)
    return render(request, 'store/cart.html', {'items': items, 'total': total})

def remove_from_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.warning(request, "You must log in to modify your cart.")
        return redirect('users:login')

    cart_item = CartItem.objects.filter(user=request.user, product_id=product_id).first()
    if cart_item:
        cart_item.delete()
        messages.success(request, "Item removed from cart.")
    return redirect('store:cart_view')

def increment_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.warning(request, "You must log in to modify your cart.")
        return redirect('users:login')

    cart_item = CartItem.objects.filter(user=request.user, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        messages.warning(request, "Item not found in your cart.")
    return redirect('store:cart_view')

def decrement_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.warning(request, "You must log in to modify your cart.")
        return redirect('users:login')

    cart_item = CartItem.objects.filter(user=request.user, product_id=product_id).first()
    if cart_item:
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
            messages.info(request, "Item removed from cart.")
        else:
            cart_item.save()
    return redirect('store:cart_view')

# -----------------------
# Checkout Page (summary)
# -----------------------
def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must log in before checking out!")
        return redirect('users:login')

    items = request.user.cart_items.all()
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect('store:cart_view')

    total = sum(item.total_price() for item in items)
    return render(request, 'store/checkout.html', {'items': items, 'total': total})

# -----------------------
# Place Order (POST only)
# -----------------------
def place_order(request):
    if not request.user.is_authenticated:
        messages.warning(request, "You must log in before placing an order!")
        return redirect('users:login')

    if request.method != "POST":
        return redirect('store:cart_view')

    items = request.user.cart_items.all()
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect('store:cart_view')

    total = sum(item.total_price() for item in items)

    order_id = get_random_string(length=8).upper()
    order = Order.objects.create(user=request.user, order_id=order_id)

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    items.delete()
    messages.success(request, "Checkout successful! Your order has been placed.")
    return render(request, 'store/checkout_success.html', {'order': order, 'total': total})
