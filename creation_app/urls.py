"""
Routes de creation_app.
Cette application gère les pages de création (POST) et la saisie du token.
"""

from django.urls import path
from . import views

app_name = "creation_app"

urlpatterns = [
    path("", views.home, name="home"),
    path("set-token/", views.set_token, name="set_token"),

    path("customers/", views.create_customer_view, name="customers"),
    path("products/", views.create_product_view, name="products"),
    path("invoices/", views.create_invoice_view, name="invoices"),
]
