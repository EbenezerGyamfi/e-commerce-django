import admin_thumbnails
from django.contrib import admin
from django.contrib.admin.templatetags.admin_modify import prepopulated_fields_js

from store.models import Product, ProductGallery, ReviewRating, Variation
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    max_num = 5

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "price",
        "stock",
        "category",
        "created_date",
        "is_available",
        "model",
    )
    prepopulated_fields = {"slug": ("product_name",)}
    inlines = [ProductGalleryInline]


class VariationAdmin(admin.ModelAdmin):
    list_display = ("product", "variation_category", "variation_value", "is_active")
    list_editable = ("is_active",)
    list_filter = ("product", "variation_category", "variation_value", "is_active")


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)
