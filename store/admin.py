from django.contrib import admin
from django.contrib.admin.templatetags.admin_modify import prepopulated_fields_js

from store.models import Product


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'created_date', 'is_available', 'model')
    prepopulated_fields = {"slug": ('product_name',)}
    

admin.site.register(Product, ProductAdmin)