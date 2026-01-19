"""
forms.py
Ce module d\'efinit les formulaires utilisés dans l\'application Pennylane Manager.
Chaque formulaire hérite de django.forms.Form et fournit des champs pour saisir
les données nécessaires à la création de clients, de produits, de factures,
ainsi qu\'un formulaire pour la recherche et un pour saisir le jeton API.
"""

from django import forms
from django.forms import formset_factory


class TokenForm(forms.Form):
    """
    Permet de saisir le jeton d\'API Pennylane. On utilise un PasswordInput
    afin de masquer la saisie de l\'utilisateur dans le navigateur.
    """
    token = forms.CharField(label="Token API", widget=forms.PasswordInput)


class CustomerForm(forms.Form):
    """Formulaire pour créer un client."""
    name = forms.CharField(label="Nom du client", max_length=255)
    email = forms.EmailField(label="Email")
    address = forms.CharField(label="Adresse", required=False)
    postal_code = forms.CharField(label="Code postal", required=False)
    city = forms.CharField(label="Ville", required=False)
    country = forms.CharField(label="Pays", initial="FR")


class InvoiceLineForm(forms.Form):
    """
    Formulaire représentant une ligne de facture (description, prix, quantité et taux de TVA).
    """
    label = forms.CharField(label="Description", max_length=255)
    unit_price = forms.DecimalField(label="Prix unitaire", min_value=0, decimal_places=2)
    quantity = forms.DecimalField(label="Quantité", min_value=0, decimal_places=2, initial=1)
    vat_rate = forms.DecimalField(label="TVA (%)", min_value=0, decimal_places=2, initial=20)


# le FormSet permet d\'avoir plusieurs lignes dynamiques dans une facture
InvoiceLineFormSet = formset_factory(InvoiceLineForm, extra=1, can_delete=True)


class InvoiceForm(forms.Form):
    """Entête du formulaire de facture (client, date, devise, statut)."""
    customer_id = forms.CharField(label="ID Client")
    date = forms.DateField(label="Date", widget=forms.DateInput(attrs={'type': 'date'}))
    currency = forms.ChoiceField(choices=[('EUR', 'EUR'), ('USD', 'USD'), ('GBP', 'GBP')], initial='EUR')
    status = forms.ChoiceField(choices=[('draft', 'Brouillon'), ('finalized', 'Finalisé')], initial='draft')


class ProductForm(forms.Form):
    """Formulaire pour créer un produit."""
    label = forms.CharField(label="Nom du produit", max_length=255)
    unit_price = forms.DecimalField(label="Prix unitaire", min_value=0, decimal_places=2)
    vat_rate = forms.DecimalField(label="TVA (%)", min_value=0, decimal_places=2, initial=20)
    currency = forms.ChoiceField(choices=[('EUR', 'EUR'), ('USD', 'USD'), ('GBP', 'GBP')], initial='EUR')


class SearchForm(forms.Form):
    """
    Formulaire permettant de rechercher des éléments (clients, factures, produits ou factures fournisseur).
    """
    TYPE_CHOICES = [
        ('company_customers', 'Clients'),
        ('customer_invoices', 'Factures'),
        ('products', 'Produits'),
        ('supplier_invoices', 'Factures fournisseurs'),
    ]
    type = forms.ChoiceField(choices=TYPE_CHOICES)
    query = forms.CharField(label="Recherche", required=False)
