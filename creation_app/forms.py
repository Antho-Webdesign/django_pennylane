"""
Formulaires Django pour les actions de création (POST).
On sépare :
- TokenForm : stocker le token Pennylane dans la session
- CustomerForm / ProductForm / InvoiceHeaderForm + InvoiceLineFormSet
"""

from django import forms
from django.forms import formset_factory


class TokenForm(forms.Form):
    token = forms.CharField(
        label="Token API Pennylane",
        required=True,
        widget=forms.PasswordInput(render_value=True),
        help_text="Le token est stocké dans la session (navigateur).",
    )


class CustomerForm(forms.Form):
    name = forms.CharField(label="Nom *", max_length=255)
    email = forms.EmailField(label="Email *")
    address = forms.CharField(label="Adresse", required=False)
    postal_code = forms.CharField(label="Code postal", required=False, max_length=20)
    city = forms.CharField(label="Ville", required=False, max_length=100)
    country = forms.CharField(label="Pays", required=False, initial="FR", max_length=2)


class ProductForm(forms.Form):
    label = forms.CharField(label="Nom du produit *", max_length=255)
    unit_price = forms.DecimalField(label="Prix unitaire *", max_digits=12, decimal_places=2)
    vat_rate = forms.CharField(label="TVA (%)", max_length=15, initial="20")
    currency = forms.ChoiceField(
        label="Devise",
        choices=[("EUR", "EUR"), ("USD", "USD"), ("GBP", "GBP")],
        initial="EUR",
    )


class InvoiceHeaderForm(forms.Form):
    customer_id = forms.CharField(label="Customer ID *", max_length=50)
    date = forms.DateField(label="Date *")
    currency = forms.ChoiceField(
        label="Devise",
        choices=[("EUR", "EUR"), ("USD", "USD"), ("GBP", "GBP")],
        initial="EUR",
    )
    status = forms.ChoiceField(
        label="Statut",
        choices=[("draft", "Brouillon"), ("finalized", "Finalisé")],
        initial="draft",
    )


class InvoiceLineForm(forms.Form):
    label = forms.CharField(label="Libellé *", max_length=255)
    unit_price = forms.DecimalField(label="Prix unitaire *", max_digits=12, decimal_places=2)
    quantity = forms.DecimalField(label="Quantité *", max_digits=12, decimal_places=2, initial=1)
    vat_rate = forms.DecimalField(label="TVA (%)", max_digits=5, decimal_places=2, initial=20)


InvoiceLineFormSet = formset_factory(InvoiceLineForm, extra=1, can_delete=True)
