from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from .models import Category, Product, CartItem, Order, OrderItem

# -----------------------
# Product / Category Views
# -----------------------
def home(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True)[:8]  # show top 8 products
    return render(request, 'store/home.html', {'categories': categories, 'products': products})

def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_active=True)
    return render(request, 'store/category_products.html', {'category': category, 'products': products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/product_detail.html', {'product': product})

# -----------------------
# Database-backed Cart Views
# -----------------------
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('store:cart_view')

@login_required
def cart_view(request):
    items = request.user.cart_items.all()
    total = sum(item.total_price() for item in items)
    return render(request, 'store/cart.html', {'items': items, 'total': total})

@login_required
def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
    cart_item.delete()
    return redirect('store:cart_view')

@login_required
def increment_cart(request, product_id):
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('store:cart_view')

@login_required
def decrement_cart(request, product_id):
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
    cart_item.quantity -= 1
    if cart_item.quantity <= 0:
        cart_item.delete()
    else:
        cart_item.save()
    return redirect('store:cart_view')

# -----------------------
# Checkout / Orders
# -----------------------
@login_required
def checkout(request):
    items = request.user.cart_items.all()
    if not items:
        return redirect('store:cart_view')

    # Calculate total
    total = sum(item.total_price() for item in items)

    # Create an Order with a random ID
    order_id = get_random_string(length=8).upper()
    order = Order.objects.create(user=request.user, order_id=order_id)

    # Add items to the order
    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    # Clear the cart
    items.delete()

    # Pass total to template to avoid template sum errors
    return render(request, 'store/checkout_success.html', {'order': order, 'total': total})
