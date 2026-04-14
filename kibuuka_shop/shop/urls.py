from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Inventory
    path('inventory/', views.inventory_list, name='inventory'),
    path('inventory/add/', views.add_product, name='add_product'),
    path('inventory/<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('inventory/<int:pk>/delete/', views.delete_product, name='delete_product'),

    # Restock
    path('inventory/restock/', views.add_stock, name='add_stock'),
    path('inventory/<int:pk>/restock/', views.add_stock, name='restock_product'),
    path('inventory/restock/history/', views.restock_history, name='restock_history'),

    # Sales
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/add/', views.add_sale, name='add_sale'),
    path('sales/<int:pk>/receipt/', views.sale_receipt, name='sale_receipt'),

    # Credit
    path('credit/', views.credit_list, name='credit_list'),
    path('credit/add/', views.add_credit, name='add_credit'),
    path('credit/<int:pk>/', views.credit_detail, name='credit_detail'),

    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.add_customer, name='add_customer'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/redeem/', views.redeem_ka_money, name='redeem_ka_money'),

    # Staff
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.add_staff, name='add_staff'),
    path('staff/<int:pk>/edit/', views.edit_staff, name='edit_staff'),

    # Reports
    path('reports/', views.reports, name='reports'),
]
