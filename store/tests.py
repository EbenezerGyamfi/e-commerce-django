import unittest
from django.test import TestCase

from store.models import Product
import platform
from django.core.management.commands.test import Command as BaseCommand

class Command(BaseCommand):
    def handle(self, *test_labels, **options):
        print(f"Python version: {platform.python_version()}")
        return super().handle(*test_labels, **options)
# Create your tests here.
class TestStoreApp(unittest.TestCase):
    def setUp(self):
        self.p = Product(product_name="product name", slug="product-name", price=123)
        
    def test_store_product(self):
        self.assertIsInstance(self.p, Product)
        
    def test_str_representation(self):
        self.assertEquals(str(self.p), "product name")
        
        

