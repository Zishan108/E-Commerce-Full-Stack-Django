from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import Category, Product

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
