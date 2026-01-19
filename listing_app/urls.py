"""
Routes de listing_app (GET).
Toutes les pages de listing sont sous /list/
"""

from django.urls import path
from . import views

app_name = "listing_app"

urlpatterns = [
    path("", views.home, name="home"),
    path("customers/", views.list_customers, name="customers"),
    path("products/", views.list_products, name="products"),
    path("customer-invoices/", views.list_customer_invoices, name="customer_invoices"),
    path("supplier-invoices/", views.list_supplier_invoices, name="supplier_invoices"),
]
