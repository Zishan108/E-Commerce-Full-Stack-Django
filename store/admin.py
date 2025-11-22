from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from decimal import Decimal
from .models import Category, Product, Order, OrderItem, CartItem

# -----------------------
# Category Admin
# -----------------------
@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

# -----------------------
# Product Admin
# -----------------------
@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    actions = ['delete_all_products']

    # -------------------
    # Add custom admin URLs
    # -------------------
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('delete-all/', self.admin_site.admin_view(self.delete_all_products_view), name='delete_all_products'),
        ]
        return custom_urls + urls

    # -------------------
    # Action dropdown option
    # -------------------
    def delete_all_products(self, request, queryset):
        """Deletes all products (action dropdown)"""
        Product.objects.all().delete()
        self.message_user(request, "All products have been deleted successfully!")
    delete_all_products.short_description = "Delete ALL Products"

    # -------------------
    # Top button view
    # -------------------
    def delete_all_products_view(self, request):
        Product.objects.all().delete()
        self.message_user(request, "All products have been deleted via button!")
        return redirect('admin:store_product_changelist')

    # -------------------
    # Add button in admin change list page
    # -------------------
    change_list_template = "admin/products_change_list.html"

# -----------------------
# Order Item Inline
# -----------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price', 'total_price_display')
    extra = 0
    
    def total_price_display(self, obj):
        return obj.total_price()
    total_price_display.short_description = 'Total Price'

# -----------------------
# Order Admin
# -----------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'get_user_email', 'created_at', 'status', 'is_paid', 'total_amount_display')
    list_filter = ('status', 'is_paid', 'created_at')
    search_fields = ('order_id', 'user__email')
    readonly_fields = ('order_id', 'user', 'created_at', 'total_amount_display')
    inlines = [OrderItemInline]
    actions = ['mark_as_pending', 'mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'
    get_user_email.admin_order_field = 'user__email'
    
    def total_amount_display(self, obj):
        return obj.total_amount()
    total_amount_display.short_description = 'Total Amount'
    
    # Status actions
    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending')
        self.message_user(request, "Selected orders marked as pending.")
    mark_as_pending.short_description = "Mark selected orders as Pending"
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, "Selected orders marked as confirmed.")
    mark_as_confirmed.short_description = "Mark selected orders as Confirmed"
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, "Selected orders marked as shipped.")
    mark_as_shipped.short_description = "Mark selected orders as Shipped"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, "Selected orders marked as delivered.")
    mark_as_delivered.short_description = "Mark selected orders as Delivered"
    
    def mark_as_cancelled(self, request, queryset):
        # Restore stock if order is cancelled
        for order in queryset:
            if order.status != 'cancelled':  # Only restore stock if not already cancelled
                for item in order.items.all():
                    product = item.product
                    product.stock += item.quantity
                    product.save()
        queryset.update(status='cancelled')
        self.message_user(request, "Selected orders marked as cancelled and stock restored.")
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled (restores stock)"

# -----------------------
# Cart Item Admin
# -----------------------
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('get_user_email', 'product', 'quantity', 'added_at', 'total_price_display')
    list_filter = ('added_at',)
    search_fields = ('user__email', 'product__name')
    
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'User Email'
    get_user_email.admin_order_field = 'user__email'
    
    def total_price_display(self, obj):
        return obj.total_price()
    total_price_display.short_description = 'Total Price'

# -----------------------
# Order Item Admin
# -----------------------
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('get_order_id', 'product', 'quantity', 'price', 'total_price_display')
    list_filter = ('order__status',)
    search_fields = ('order__order_id', 'product__name')
    
    def get_order_id(self, obj):
        return obj.order.order_id
    get_order_id.short_description = 'Order ID'
    get_order_id.admin_order_field = 'order__order_id'
    
    def total_price_display(self, obj):
        return obj.total_price()
    total_price_display.short_description = 'Total Price'