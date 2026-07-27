from django.contrib import admin
from .models import Salesperson, Customer, Product, Sale

# Register your models here.
@admin.register(Salesperson)
class SalespersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'gender', 'email', 'region', 'phone')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'gender', 'company', 'city', 'state')
    search_fields = ('first_name', 'last_name', 'company', 'email')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'sku')
    list_filter = ('category',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('customer', 'salesperson', 'product', 'quantity', 'date', 'status')
    list_filter = ('status', 'salesperson', 'product__category', 'date')
    date_hierarchy = 'date'