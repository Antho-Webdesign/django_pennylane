"""
urls.py
Définit les routes pour l'application manager. Chaque chemin est associé à une vue.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('set-token/', views.set_token, name='set_token'),
    path('customers/', views.customers, name='customers'),
    path('invoices/', views.invoices, name='invoices'),
    path('products/', views.products, name='products'),
    path('search/', views.search, name='search'),
]
