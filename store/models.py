from pyexpat import model
from typing import NamedTuple
from django.core.cache import cache
from django.db import models
from django.urls import reverse
from category.models import Category

# Create your models here.
class Product(models.Model):
    SHIRT_SIZES = {
        "S": "Small",
        "M": "Medium",
        "L": "Large",
    }
       
    product_name = models.CharField('product first name',max_length=200, unique=True, default="testing product", help_text="this is the product name")
    slug = models.SlugField(max_length=200, unique=True)
    product_description = models.TextField(blank=True, null=True,)
    price = models.IntegerField()
    images = models.ImageField(upload_to="photos/products")
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    
    
 
    

    @classmethod
    def products(cls):
        cache_key = "available_products"

        products = cache.get(cache_key)

        if not products:
            products = cls.objects.filter(is_available=True)
            cache.set(cache_key, products, 60 * 60)  # Cache for 1 hour

        return products
    
    def get_url(self):
        return reverse('product_details', args=[self.category.slug, self.slug])
        
    def __str__(self):
        return self.product_name
    
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)
    

variation_category_choice = (
    ('color', 'color'),
    ('size', 'size')
)
    
class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(choices=variation_category_choice, max_length=100,)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    objects = VariationManager()
    
    def __str__(self):
        return self.variation_value
    

# class Variation(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     variation_category = models.CharField(choices=variation_category_choice, max_length=100,)
#     variation_value = models.CharField(max_length=100)
#     is_active = models.BooleanField(default=True)
#     created_date = models.DateTimeField(auto_now_add=True)