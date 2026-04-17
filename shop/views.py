from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta, date
from .models import (
    ShopAssistant, Category, Product, RestockRecord,
    Customer, CreditTransaction, CreditPayment, Sale, KaMoneyRedemption
)
from .forms import (
    LoginForm, ProductForm, RestockForm, SaleForm,
    CreditTransactionForm, CreditPaymentForm,
    CustomerForm, ShopAssistantForm
)


# ──────────────────────────────────────────────
#  AUTHENTICATION
# ──────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'shop/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ──────────────────────────────────────────────
#  DASHBOARD
# ──────────────────────────────────────────────
@login_required
def dashboard(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    # Sales summary
    today_sales = Sale.objects.filter(sold_at__date=today)
    today_revenue = today_sales.aggregate(total=Sum('total_amount'))['total'] or 0
    weekly_sales = Sale.objects.filter(sold_at__date__gte=week_ago)
    weekly_revenue = weekly_sales.aggregate(total=Sum('total_amount'))['total'] or 0

    # Inventory alerts
    low_stock_items = Product.objects.filter(
        stock_quantity__lte=F('low_stock_threshold')
    ).count()
    out_of_stock = Product.objects.filter(stock_quantity=0).count()

    # Credit summary
    total_outstanding = CreditTransaction.objects.filter(
        status__in=['unpaid', 'partial']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    overdue_credits = CreditTransaction.objects.filter(
        status__in=['unpaid', 'partial'],
        repayment_date__lt=today
    ).count()

    # Top 5 products today
    top_products = (
        Sale.objects.filter(sold_at__date__gte=week_ago)
        .values('product__name')
        .annotate(total_qty=Sum('quantity'), total_rev=Sum('total_amount'))
        .order_by('-total_qty')[:5]
    )

    # Recent sales
    recent_sales = Sale.objects.select_related('product', 'sold_by').order_by('-sold_at')[:10]

    # Payment breakdown this week
    payment_breakdown = weekly_sales.values('payment_method').annotate(
        count=Count('id'), total=Sum('total_amount')
    )

    context = {
        'today_revenue': today_revenue,
        'weekly_revenue': weekly_revenue,
        'today_sales_count': today_sales.count(),
        'low_stock_items': low_stock_items,
        'out_of_stock': out_of_stock,
        'total_outstanding': total_outstanding,
        'overdue_credits': overdue_credits,
        'top_products': top_products,
        'recent_sales': recent_sales,
        'payment_breakdown': payment_breakdown,
        'total_products': Product.objects.count(),
    }
    return render(request, 'shop/dashboard.html', context)


# ──────────────────────────────────────────────
#  INVENTORY
# ──────────────────────────────────────────────
@login_required
def inventory_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    stock_filter = request.GET.get('stock', '')

    products = Product.objects.select_related('category').all()

    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(category_id=category_id)
    if stock_filter == 'low':
        products = products.filter(stock_quantity__lte=F('low_stock_threshold'))
    elif stock_filter == 'out':
        products = products.filter(stock_quantity=0)

    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'stock_filter': stock_filter,
    }
    return render(request, 'shop/inventory.html', context)


@login_required
def add_product(request):
    form = ProductForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product added successfully!')
        return redirect('inventory')
    return render(request, 'shop/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{product.name} updated!')
        return redirect('inventory')
    return render(request, 'shop/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})


@login_required
def delete_product(request, pk):
    # Only owners/admins can delete
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to delete products.')
        return redirect('inventory')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted.')
        return redirect('inventory')
    return render(request, 'shop/confirm_delete.html', {'object': product, 'type': 'Product'})


# ──────────────────────────────────────────────
#  RESTOCK
# ──────────────────────────────────────────────
@login_required
def add_stock(request, pk=None):
    product = get_object_or_404(Product, pk=pk) if pk else None
    form = RestockForm(request.POST or None, initial={'product': product})
    if request.method == 'POST' and form.is_valid():
        restock = form.save(commit=False)
        restock.restocked_by = request.user
        restock.save()
        # Update product stock
        restock.product.stock_quantity += restock.quantity_added
        restock.product.save()
        messages.success(request, f'Stock updated for {restock.product.name}!')
        return redirect('inventory')
    return render(request, 'shop/restock_form.html', {'form': form, 'product': product})


@login_required
def restock_history(request):
    records = RestockRecord.objects.select_related('product', 'restocked_by').order_by('-restocked_at')
    return render(request, 'shop/restock_history.html', {'records': records})


# ──────────────────────────────────────────────
#  SALES
# ──────────────────────────────────────────────
@login_required
def add_sale(request):
    form = SaleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        sale = form.save(commit=False)
        sale.sold_by = request.user

        # Check stock availability
        if sale.product.stock_quantity < sale.quantity:
            messages.error(request, f'Not enough stock! Only {sale.product.stock_quantity} {sale.product.unit}(s) available.')
        else:
            sale.unit_price = sale.product.selling_price
            sale.save()

            # Decrement product stock after a successful sale
            sale.product.stock_quantity -= sale.quantity
            sale.product.save()

            messages.success(request, f'Sale recorded! {sale.product.name} x{sale.quantity}')

            if sale.payment_method == 'credit':
                if sale.customer:
                    CreditTransaction.objects.create(
                        customer=sale.customer,
                        product=sale.product,
                        quantity=sale.quantity,
                        unit_price=sale.unit_price,
                        total_amount=sale.total_amount,
                        amount_paid=0,
                        repayment_date=timezone.now().date() + timedelta(days=30),
                        status='unpaid',
                        recorded_by=request.user,
                        notes=sale.notes or 'Auto-created from sale record'
                    )
                    messages.info(request, f'Credit record automatically created for {sale.customer.name}.')
                else:
                    messages.warning(request, 'Credit sale recorded but no customer was selected. Please add the credit record manually.')
                return redirect('credit_list')

            if sale.payment_method in ('cash', 'mobile_money'):
                return redirect('sale_receipt', pk=sale.pk)

            return redirect('sales_list')

    return render(request, 'shop/sale_form.html', {'form': form, 'title': 'Add Sale'})

@login_required
def sales_list(request):
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')
    payment = request.GET.get('payment', '')

    sales = Sale.objects.select_related('product', 'customer', 'sold_by').order_by('-sold_at')

    if date_from:
        sales = sales.filter(sold_at__date__gte=date_from)
    if date_to:
        sales = sales.filter(sold_at__date__lte=date_to)
    if payment:
        sales = sales.filter(payment_method=payment)

    total_revenue = sales.aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'sales': sales,
        'total_revenue': total_revenue,
        'date_from': date_from,
        'date_to': date_to,
        'payment': payment,
    }
    return render(request, 'shop/sales_list.html', context)


# ──────────────────────────────────────────────
#  CREDIT MANAGEMENT
# ──────────────────────────────────────────────
@login_required
def credit_list(request):
    status = request.GET.get('status', '')
    credits = CreditTransaction.objects.select_related('customer', 'product').order_by('-date_issued')
    if status:
        credits = credits.filter(status=status)
    total_outstanding = credits.filter(
        status__in=['unpaid', 'partial']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    context = {
        'credits': credits,
        'total_outstanding': total_outstanding,
        'status': status,
    }
    return render(request, 'shop/credit_list.html', context)


@login_required
def add_credit(request):
    # Assistants cannot modify credit records
    try:
        assistant = request.user.shopassistant
        messages.error(request, 'Shop assistants cannot create credit records.')
        return redirect('credit_list')
    except ShopAssistant.DoesNotExist:
        pass

    form = CreditTransactionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        credit = form.save(commit=False)
        credit.recorded_by = request.user
        credit.save()
        messages.success(request, f'Credit recorded for {credit.customer.name}!')
        return redirect('credit_list')
    return render(request, 'shop/credit_form.html', {'form': form, 'title': 'Add Credit'})


@login_required
def credit_detail(request, pk):
    credit = get_object_or_404(CreditTransaction, pk=pk)
    payments = credit.payments.all().order_by('-paid_at')
    pay_form = CreditPaymentForm(request.POST or None)

    if request.method == 'POST' and pay_form.is_valid():
        payment = pay_form.save(commit=False)
        payment.credit = credit
        payment.received_by = request.user
        payment.save()
        # Update credit amount_paid
        credit.amount_paid += payment.amount
        credit.save()
        messages.success(request, f'Payment of {payment.amount} UGX recorded!')
        return redirect('credit_detail', pk=pk)

    context = {'credit': credit, 'payments': payments, 'pay_form': pay_form}
    return render(request, 'shop/credit_detail.html', context)


# ──────────────────────────────────────────────
#  CUSTOMERS
# ──────────────────────────────────────────────
@login_required
def customer_list(request):
    query = request.GET.get('q', '')
    customers = Customer.objects.all()
    if query:
        customers = customers.filter(name__icontains=query)
    return render(request, 'shop/customer_list.html', {'customers': customers, 'query': query})


@login_required
def add_customer(request):
    form = CustomerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Customer added!')
        return redirect('customer_list')
    return render(request, 'shop/customer_form.html', {'form': form})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    credits = customer.credits.order_by('-date_issued')
    sales = Sale.objects.filter(customer=customer).order_by('-sold_at')
    redemptions = customer.redemptions.all().order_by('-redeemed_at')
    context = {
        'customer': customer,
        'credits': credits,
        'sales': sales,
        'redemptions': redemptions,
    }
    return render(request, 'shop/customer_detail.html', context)


@login_required
def redeem_ka_money(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if not customer.ka_money_redeemable:
        messages.error(request, 'Customer is not eligible for Ka Money redemption yet.')
        return redirect('customer_detail', pk=pk)
    if request.method == 'POST':
        amount = customer.ka_money_balance
        KaMoneyRedemption.objects.create(
            customer=customer,
            amount_redeemed=amount,
            processed_by=request.user
        )
        customer.ka_money_balance = 0
        customer.mobile_money_purchases = 0
        customer.save()
        messages.success(request, f'{customer.name} redeemed {amount} UGX Ka Money!')
        return redirect('customer_detail', pk=pk)
    return render(request, 'shop/redeem_confirm.html', {'customer': customer})


# ──────────────────────────────────────────────
#  STAFF MANAGEMENT
# ──────────────────────────────────────────────
@login_required
def staff_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Access restricted to managers.')
        return redirect('dashboard')
    assistants = ShopAssistant.objects.all()
    return render(request, 'shop/staff_list.html', {'assistants': assistants})


@login_required
def add_staff(request):
    if not request.user.is_staff:
        messages.error(request, 'Access restricted.')
        return redirect('dashboard')
    form = ShopAssistantForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Staff member added!')
        return redirect('staff_list')
    return render(request, 'shop/staff_form.html', {'form': form, 'title': 'Add Staff'})


@login_required
def edit_staff(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Access restricted.')
        return redirect('dashboard')
    assistant = get_object_or_404(ShopAssistant, pk=pk)
    form = ShopAssistantForm(request.POST or None, instance=assistant)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Staff updated!')
        return redirect('staff_list')
    return render(request, 'shop/staff_form.html', {'form': form, 'title': 'Edit Staff', 'assistant': assistant})


# ──────────────────────────────────────────────
#  REPORTS
# ──────────────────────────────────────────────
@login_required
def reports(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    # Top 10 selling items this week
    top_10 = (
        Sale.objects.filter(sold_at__date__gte=week_ago)
        .values('product__name', 'product__category__name')
        .annotate(total_qty=Sum('quantity'), total_rev=Sum('total_amount'))
        .order_by('-total_qty')[:10]
    )

    # Revenue this week
    weekly_revenue = Sale.objects.filter(
        sold_at__date__gte=week_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # Expenses (cost of goods sold)
    weekly_cogs = sum(
        s.quantity * s.product.buying_price
        for s in Sale.objects.filter(
            sold_at__date__gte=week_ago
        ).select_related('product')
        if s.product
    )

    # Outstanding credit
    outstanding_credit = CreditTransaction.objects.filter(
        status__in=['unpaid', 'partial']
    ).aggregate(total=Sum(F('total_amount') - F('amount_paid')))['total'] or 0

    # Overdue credits
    overdue = CreditTransaction.objects.filter(
        status__in=['unpaid', 'partial'],
        repayment_date__lt=today
    ).select_related('customer')

    # Low stock alerts
    low_stock = Product.objects.filter(
        stock_quantity__lte=F('low_stock_threshold')
    ).order_by('stock_quantity')

    # Sales by payment method
    payment_stats = Sale.objects.filter(
        sold_at__date__gte=week_ago
    ).values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    )

    # Daily revenue for the week (for chart)
    daily_revenue = []
    for i in range(7):
        day = today - timedelta(days=6 - i)
        rev = Sale.objects.filter(sold_at__date=day).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        daily_revenue.append({'day': day.strftime('%a'), 'revenue': float(rev)})

    context = {
        'top_10': top_10,
        'weekly_revenue': weekly_revenue,
        'weekly_cogs': weekly_cogs,
        'weekly_profit': weekly_revenue - weekly_cogs,
        'outstanding_credit': outstanding_credit,
        'overdue': overdue,
        'low_stock': low_stock,
        'payment_stats': payment_stats,
        'daily_revenue': daily_revenue,
        'week_ago': week_ago,
        'today': today,
    }
    return render(request, 'shop/reports.html', context)


# ──────────────────────────────────────────────
#  RECEIPT
# ──────────────────────────────────────────────
@login_required
def sale_receipt(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    # Credit sales do not generate receipts
    if sale.payment_method == 'credit':
        messages.error(request, 'Credit sales do not generate receipts.')
        return redirect('sales_list')
    return render(request, 'shop/receipt.html', {'sale': sale})
