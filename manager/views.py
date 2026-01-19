"""
views.py
Ce fichier contient les vues pour l'application Pennylane Manager.
Chaque vue gère la validation des formulaires et appelle la couche de services
pour interagir avec l'API Pennylane. Les messages de succès ou d'erreur
sont envoyés via django.contrib.messages.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import (
    TokenForm, CustomerForm, InvoiceForm, InvoiceLineFormSet,
    ProductForm, SearchForm,
)
from .services import create_customer, create_invoice, create_product, search_entities


def index(request):
    """
    Redirige la page d'accueil vers l'onglet clients.
    """
    return redirect('customers')


def set_token(request):
    """
    Affiche un formulaire permettant à l'utilisateur de saisir son jeton API.
    Le jeton est enregistré en session et utilisé lors des appels à l'API.
    """
    if request.method == 'POST':
        form = TokenForm(request.POST)
        if form.is_valid():
            # stocke le token dans la session utilisateur
            request.session['pennylane_token'] = form.cleaned_data['token']
            messages.success(request, "Jeton enregistré avec succès.")
            return redirect('customers')
    else:
        form = TokenForm(initial={'token': request.session.get('pennylane_token', '')})
    return render(request, 'manager/set_token.html', {'form': form})


def customers(request):
    """
    Vue pour créer un client.
    Affiche le formulaire et envoie les données à l'API en cas de POST.
    """
    result = None
    # récupère le token dans la session ou None si inexistant
    token = request.session.get('pennylane_token')
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            try:
                # appel de la couche de services avec le token
                result = create_customer(form.cleaned_data, token=token)
                messages.success(request, 'Client créé avec succès.')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = CustomerForm()
    return render(request, 'manager/customers.html', {'form': form, 'result': result})


def invoices(request):
    """
    Vue pour créer une facture avec plusieurs lignes.
    Utilise un formset pour gérer les lignes de facture.
    """
    result = None
    token = request.session.get('pennylane_token')
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceLineFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            try:
                # on récupère les lignes non supprimées du formset
                lines = [
                    line_form.cleaned_data for line_form in formset.forms
                    if not line_form.cleaned_data.get('DELETE', False)
                ]
                result = create_invoice(form.cleaned_data, lines, token=token)
                messages.success(request, 'Facture créée avec succès.')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = InvoiceForm()
        formset = InvoiceLineFormSet()
    return render(request, 'manager/invoices.html', {
        'form': form, 'formset': formset, 'result': result
    })


def products(request):
    """
    Vue pour créer un produit.
    """
    result = None
    token = request.session.get('pennylane_token')
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                result = create_product(form.cleaned_data, token=token)
                messages.success(request, 'Produit créé avec succès.')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = ProductForm()
    return render(request, 'manager/products.html', {'form': form, 'result': result})


def search(request):
    """
    Vue pour effectuer des recherches sur différents types d'entités.
    """
    result = None
    token = request.session.get('pennylane_token')
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            entity_type = form.cleaned_data['type']
            query = form.cleaned_data['query']
            try:
                result = search_entities(entity_type, query, token=token)
                messages.success(request, 'Recherche terminée.')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = SearchForm()
    return render(request, 'manager/search.html', {'form': form, 'result': result})
