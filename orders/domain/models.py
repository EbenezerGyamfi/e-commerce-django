from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from accounts.models import Account
from store.models import Product, Variation


class Payment(models.Model):
    PAYMENT_STATUS = (
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    )

    PAYMENT_METHODS = (
        ("PAYPAL", "PayPal"),
        ("STRIPE", "Stripe"),
        ("CASH", "Cash on Delivery"),
    )

    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="payments")
    payment_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")

    def __str__(self):
        return f"{self.payment_id} - {self.amount_paid}"

    def process_payment(self):
        """Process the payment and update status."""
        # Payment processing logic here
        self.status = "COMPLETED"
        self.save()

    def refund(self):
        """Refund the payment."""
        self.status = "REFUNDED"
        self.save()


class Order(models.Model):
    STATUS = (
        ("NEW", "New"),
        ("ACCEPTED", "Accepted"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    )

    user = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, related_name="orders"
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True, related_name="orders"
    )
    order_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in the format: '+999999999'",
            )
        ],
    )
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    tax = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    status = models.CharField(max_length=10, choices=STATUS, default="NEW")
    ip = models.GenericIPAddressField(blank=True, null=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2 or ""}'.strip()

    def get_total_items(self):
        return sum(item.quantity for item in self.order_products.all())

    def calculate_totals(self):
        """Calculate order totals including tax."""
        subtotal = sum(item.total_price for item in self.order_products.all())
        tax = (Decimal("2.00") * subtotal) / Decimal("100.00")
        return {"subtotal": subtotal, "tax": tax, "total": subtotal + tax}

    def accept_order(self):
        """Accept the order and update status."""
        self.status = "ACCEPTED"
        self.save()

    def complete_order(self):
        """Mark order as completed."""
        self.status = "COMPLETED"
        self.save()

    def cancel_order(self):
        """Cancel the order."""
        self.status = "CANCELLED"
        self.save()

    def __str__(self):
        return f"{self.order_number} - {self.full_name()}"


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_products"
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True
    )
    user = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="order_products"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_products"
    )
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    product_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Order Product")
        verbose_name_plural = _("Order Products")

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity}"

    @property
    def total_price(self):
        return self.product_price * self.quantity

    def update_stock(self):
        """Update product stock after order."""
        self.product.stock -= self.quantity
        self.product.save()
