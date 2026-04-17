from django import forms
from .models import (
    Product, RestockRecord, Sale, CreditTransaction,
    CreditPayment, Customer, ShopAssistant, Category
)


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
        })
    )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'buying_price', 'selling_price',
                  'unit', 'stock_quantity', 'low_stock_threshold', 'is_essential']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'buying_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5'}),
            'is_essential': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RestockForm(forms.ModelForm):
    class Meta:
        model = RestockRecord
        fields = ['product', 'quantity_added', 'buying_price_at_restock', 'supplier_name', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity_added': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'buying_price_at_restock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'supplier_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier name (optional)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notes...'}),
        }


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity', 'payment_method', 'customer', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select', 'id': 'id_product'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': '1'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['customer'].required = False
    self.fields['customer'].empty_label = "— Walk-in customer —"
    self.fields['notes'].required = False

def clean(self):
    cleaned_data = super().clean()
    payment_method = cleaned_data.get('payment_method')
    customer = cleaned_data.get('customer')
    if payment_method == 'credit' and not customer:
        self.add_error('customer', 'You must select a customer for credit sales.')
    return cleaned_data

class CreditTransactionForm(forms.ModelForm):
    class Meta:
        model = CreditTransaction
        fields = ['customer', 'product', 'quantity', 'unit_price', 'repayment_date', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'repayment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class CreditPaymentForm(forms.ModelForm):
    class Meta:
        model = CreditPayment
        fields = ['amount', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Amount paid (UGX)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notes...'}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'contact', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0700 000000'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Area / street'}),
        }


class ShopAssistantForm(forms.ModelForm):
    class Meta:
        model = ShopAssistant
        fields = ['name', 'age', 'contact', 'start_date', 'shift', 'daily_wage', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': '18'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'shift': forms.Select(attrs={'class': 'form-select'}),
            'daily_wage': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
