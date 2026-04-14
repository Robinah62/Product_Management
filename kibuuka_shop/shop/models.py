
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ──────────────────────────────────────────────
#  STAFF / SHOP ASSISTANT
# ──────────────────────────────────────────────
class ShopAssistant(models.Model):
    SHIFT_CHOICES = [
        ('morning', 'Morning (6am – 2pm)'),
        ('afternoon', 'Afternoon (2pm – 10pm)'),
        ('full', 'Full Day'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    contact = models.CharField(max_length=20)
    start_date = models.DateField()
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default='morning')
    daily_wage = models.DecimalField(max_digits=10, decimal_places=2, default=8000)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Shop Assistant"


# ──────────────────────────────────────────────
#  PRODUCT CATEGORY
# ──────────────────────────────────────────────
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


# ──────────────────────────────────────────────
#  PRODUCT / INVENTORY
# ──────────────────────────────────────────────
class Product(models.Model):
    UNIT_CHOICES = [
        ('piece', 'Piece'),
        ('kg', 'Kilogram'),
        ('litre', 'Litre'),
        ('packet', 'Packet'),
        ('dozen', 'Dozen'),
        ('bundle', 'Bundle'),
        ('box', 'Box'),
    ]
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='piece')
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    is_essential = models.BooleanField(default=False, help_text="Mark if this is an essential item needing alerts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.stock_quantity} {self.unit})"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold

    @property
    def profit_margin(self):
        if self.buying_price > 0:
            return ((self.selling_price - self.buying_price) / self.buying_price) * 100
        return 0

    class Meta:
        ordering = ['name']


# ──────────────────────────────────────────────
#  RESTOCK HISTORY
# ──────────────────────────────────────────────
class RestockRecord(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='restock_records')
    quantity_added = models.PositiveIntegerField()
    buying_price_at_restock = models.DecimalField(max_digits=10, decimal_places=2)
    supplier_name = models.CharField(max_length=100, blank=True)
    restocked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    restocked_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product.name} +{self.quantity_added} on {self.restocked_at.date()}"

    class Meta:
        ordering = ['-restocked_at']


# ──────────────────────────────────────────────
#  CUSTOMER (for credit & Ka Money)
# ──────────────────────────────────────────────
class Customer(models.Model):
    name = models.CharField(max_length=150)
    contact = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200, blank=True)
    # Ka Money savings wallet
    ka_money_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mobile_money_purchases = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def ka_money_redeemable(self):
        """Ka Money is redeemable after 10 mobile money purchases."""
        return self.mobile_money_purchases >= 10 and self.ka_money_balance > 0


# ──────────────────────────────────────────────
#  CREDIT TRANSACTION
# ──────────────────────────────────────────────
class CreditTransaction(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Fully Paid'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='credits')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_issued = models.DateField(default=timezone.now)
    repayment_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.customer.name} – {self.product} – {self.status}"

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid

    def save(self, *args, **kwargs):
        self.total_amount = self.unit_price * self.quantity
        if self.amount_paid >= self.total_amount:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        else:
            self.status = 'unpaid'
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date_issued']


# ──────────────────────────────────────────────
#  CREDIT PAYMENT (installments)
# ──────────────────────────────────────────────
class CreditPayment(models.Model):
    credit = models.ForeignKey(CreditTransaction, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(default=timezone.now)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Payment of {self.amount} for {self.credit}"


# ──────────────────────────────────────────────
#  SALE
# ──────────────────────────────────────────────
class Sale(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money'),
        ('credit', 'Credit'),
    ]
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    sold_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    sold_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.unit_price * self.quantity
        # Reduce stock
        if self.product and not self.pk:  # only on creation
            self.product.stock_quantity -= self.quantity
            self.product.save()
        # Ka Money: earn 500 UGX for every mobile money transaction
        if self.payment_method == 'mobile_money' and self.customer:
            self.customer.ka_money_balance += 500
            self.customer.mobile_money_purchases += 1
            self.customer.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale #{self.pk} – {self.product} x{self.quantity}"

    class Meta:
        ordering = ['-sold_at']


# ──────────────────────────────────────────────
#  KA MONEY REDEMPTION
# ──────────────────────────────────────────────
class KaMoneyRedemption(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='redemptions')
    amount_redeemed = models.DecimalField(max_digits=10, decimal_places=2)
    redeemed_at = models.DateTimeField(default=timezone.now)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.customer.name} redeemed {self.amount_redeemed} UGX"
