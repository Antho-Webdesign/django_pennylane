"""
Vues GET : listing simple de chaque ressource.
Les résultats JSON sont affichés dans les templates.
"""

from django.shortcuts import render
from django.contrib import messages

from .forms import NameFilterForm
from .services import list_entities


def _get_session_token(request) -> str | None:
    return request.session.get("PENNYLANE_TOKEN")


def home(request):
    return render(request, "listing_app/home.html")


def _generic_list(request, entity_type: str, title: str):
    token = _get_session_token(request)
    form = NameFilterForm(request.GET)

    q = ""
    if form.is_valid():
        q = form.cleaned_data.get("q") or ""

    try:
        result = list_entities(entity_type=entity_type, q=q, token=token)
    except Exception as e:
        messages.error(request, f"Erreur: {e}")
        result = None

    return render(
        request,
        "listing_app/list.html",
        {
            "title": title,
            "form": form,
            "result": result,
            "entity_type": entity_type,
        },
    )


def list_customers(request):
    return _generic_list(request, "company_customers", "Liste des clients")


def list_products(request):
    return _generic_list(request, "products", "Liste des produits")


def list_customer_invoices(request):
    return _generic_list(request, "customer_invoices", "Liste des factures clients")


def list_supplier_invoices(request):
    return _generic_list(request, "supplier_invoices", "Liste des factures fournisseurs")
