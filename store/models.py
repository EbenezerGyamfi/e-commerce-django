from django.core.cache import cache
from django.db import models
from category.models import Category

# Create your models here.
class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    product_description = models.TextField(blank=True)
    price = models.IntegerField()
    images = models.ImageField(upload_to="photos/products")
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    

    @classmethod
    def products(cls):
        cache_key = "available_products"

        products = cache.get(cache_key)

        if not products:
            products = cls.objects.filter(is_available=True)
            cache.set(cache_key, products, 60 * 60)  # Cache for 1 hour

        return products
        
    def __str__(self):
        return self.product_name