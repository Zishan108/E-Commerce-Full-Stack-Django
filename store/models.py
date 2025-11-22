from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from decimal import Decimal

# -----------------------
# Categories & Products
# -----------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# -----------------------
# Cart Items
# -----------------------
class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    def total_price(self):
        if self.quantity is None or self.product.price is None:
            return Decimal('0.00')
        return self.product.price * self.quantity

# -----------------------
# Orders & Order Items
# -----------------------
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    order_id = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        # Use email instead of username since custom User model might not have username
        user_identifier = self.user.email if hasattr(self.user, 'email') else f"User {self.user.id}"
        return f"Order #{self.order_id} by {user_identifier}"

    def total_amount(self):
        """Calculate total amount for the order"""
        total = Decimal('0.00')
        for item in self.items.all():
            item_total = item.total_price()
            if item_total is not None:
                total += item_total
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def total_price(self):
        if self.quantity is None or self.price is None:
            return Decimal('0.00')
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (Order #{self.order.order_id})"

    def save(self, *args, **kwargs):
        # If price is not set, use the product's current price
        if self.price is None or self.price == 0:
            self.price = self.product.price
        super().save(*args, **kwargs)