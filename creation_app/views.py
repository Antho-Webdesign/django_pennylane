"""
Vues HTML de creation_app :
- set_token : enregistre le token en session
- create_customer_view / create_product_view / create_invoice_view : formulaires + POST
"""

from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import (
    TokenForm,
    CustomerForm,
    ProductForm,
    InvoiceHeaderForm,
    InvoiceLineFormSet,
)
from .services import create_customer, create_product, create_invoice


def _get_session_token(request) -> str | None:
    """Récupère le token Pennylane stocké en session."""
    return request.session.get("PENNYLANE_TOKEN")


def home(request):
    return render(request, "creation_app/home.html")


def set_token(request):
    if request.method == "POST":
        form = TokenForm(request.POST)
        if form.is_valid():
            request.session["PENNYLANE_TOKEN"] = form.cleaned_data["token"]
            messages.success(request, "Token enregistré en session ✅")
            return redirect("creation_app:home")
    else:
        form = TokenForm(initial={"token": _get_session_token(request) or ""})

    return render(request, "creation_app/set_token.html", {"form": form})


def create_customer_view(request):
    token = _get_session_token(request)

    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            payload = {
                "name": form.cleaned_data["name"],
                "emails": [form.cleaned_data["email"]],
                "billing_address": {
                    "address": form.cleaned_data.get("address", ""),
                    "postal_code": form.cleaned_data.get("postal_code", ""),
                    "city": form.cleaned_data.get("city", ""),
                    "country": form.cleaned_data.get("country", "FR") or "FR",
                },
            }
            try:
                result = create_customer(payload, token)
                messages.success(request, "Client créé ✅")
                return render(request, "creation_app/customers.html", {"form": form, "result": result})
            except Exception as e:
                messages.error(request, f"Erreur: {e}")
    else:
        form = CustomerForm()

    return render(request, "creation_app/customers.html", {"form": form})


def create_product_view(request):
    token = _get_session_token(request)

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            payload = {
                "label": form.cleaned_data["label"],
                "unit_price": float(form.cleaned_data["unit_price"]),
                "vat_rate": float(form.cleaned_data["vat_rate"]),
                "currency": form.cleaned_data["currency"],
            }
            try:
                result = create_product(payload, token)
                messages.success(request, "Produit créé ✅")
                return render(request, "creation_app/products.html", {"form": form, "result": result})
            except Exception as e:
                messages.error(request, f"Erreur: {e}")
    else:
        form = ProductForm()

    return render(request, "creation_app/products.html", {"form": form})


def create_invoice_view(request):
    token = _get_session_token(request)

    if request.method == "POST":
        header_form = InvoiceHeaderForm(request.POST)
        line_formset = InvoiceLineFormSet(request.POST)

        if header_form.is_valid() and line_formset.is_valid():
            # Lignes non supprimées
            lines = []
            for f in line_formset:
                if f.cleaned_data and not f.cleaned_data.get("DELETE"):
                    lines.append(f.cleaned_data)

            payload = {
                "customer_id": header_form.cleaned_data["customer_id"],
                "date": header_form.cleaned_data["date"].isoformat(),
                "currency": header_form.cleaned_data["currency"],
                "status": header_form.cleaned_data["status"],
                # Pennylane v2 attend "line_items"
                "line_items": [
                    {
                        "label": l["label"],
                        "unit_price": float(l["unit_price"]),
                        "quantity": float(l["quantity"]),
                        "vat_rate": float(l["vat_rate"]),
                    }
                    for l in lines
                ],
            }

            try:
                result = create_invoice(payload, token)
                messages.success(request, "Facture créée ✅")
                return render(
                    request,
                    "creation_app/invoices.html",
                    {"header_form": header_form, "line_formset": line_formset, "result": result},
                )
            except Exception as e:
                messages.error(request, f"Erreur: {e}")
    else:
        header_form = InvoiceHeaderForm()
        line_formset = InvoiceLineFormSet()

    return render(
        request,
        "creation_app/invoices.html",
        {"header_form": header_form, "line_formset": line_formset},
    )
