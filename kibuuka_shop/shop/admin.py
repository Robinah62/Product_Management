from django.contrib import admin
from .models import (
    ShopAssistant, Category, Product, RestockRecord,
    Customer, CreditTransaction, CreditPayment, Sale, KaMoneyRedemption
)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'buying_price', 'selling_price', 'stock_quantity', 'is_low_stock', 'is_essential']
    list_filter = ['category', 'is_essential']
    search_fields = ['name']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'total_amount', 'payment_method', 'sold_by', 'sold_at']
    list_filter = ['payment_method', 'sold_at']

@admin.register(CreditTransaction)
class CreditAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'total_amount', 'amount_paid', 'status', 'repayment_date']
    list_filter = ['status']

admin.site.register(ShopAssistant)
admin.site.register(Category)
admin.site.register(RestockRecord)
admin.site.register(Customer)
admin.site.register(CreditPayment)
admin.site.register(KaMoneyRedemption)

admin.site.site_header = "Kibuuka's Corner Shop Admin"
admin.site.site_title = "Shop Admin"
admin.site.index_title = "Shop Management"
