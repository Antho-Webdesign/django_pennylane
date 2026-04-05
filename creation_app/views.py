import logging
from typing import Any

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .forms import (
    TokenForm,
    CustomerForm,
    ProductForm,
    InvoiceHeaderForm,
    InvoiceLineFormSet,
)
from .services import create_customer, create_product, create_invoice

logger = logging.getLogger(__name__)

SESSION_TOKEN_KEY = "PENNYLANE_TOKEN"


def _get_session_token(request: HttpRequest) -> str | None:
    """Retourne le token Pennylane stocké en session."""
    return request.session.get(SESSION_TOKEN_KEY)


def _require_session_token(request: HttpRequest) -> str | None:
    """
    Retourne le token Pennylane si présent.
    Ajoute un message d'erreur sinon.
    """
    token = _get_session_token(request)
    if not token:
        messages.error(request, "Aucun token Pennylane en session. Veuillez le renseigner d'abord.")
    return token


def _handle_service_error(request: HttpRequest, action_label: str, exc: Exception) -> None:
    """Journalise l'erreur et affiche un message utilisateur."""
    logger.exception("Erreur lors de l'action '%s'", action_label)
    messages.error(request, f"{action_label} impossible : {exc}")


def _build_customer_payload(form: CustomerForm) -> dict[str, Any]:
    cleaned = form.cleaned_data
    return {
        "name": cleaned["name"],
        "emails": [cleaned["email"]],
        "billing_address": {
            "address": cleaned.get("address", ""),
            "postal_code": cleaned.get("postal_code", ""),
            "city": cleaned.get("city", ""),
            "country": cleaned.get("country") or "FR",
        },
    }


def _build_product_payload(form: ProductForm) -> dict[str, Any]:
    cleaned = form.cleaned_data
    return {
        "label": cleaned["label"],
        "unit_price": float(cleaned["unit_price"]),
        "vat_rate": float(cleaned["vat_rate"]),
        "currency": cleaned["currency"],
    }


def _get_active_invoice_lines(line_formset: InvoiceLineFormSet) -> list[dict[str, Any]]:
    """Retourne uniquement les lignes valides non supprimées."""
    return [
        form.cleaned_data
        for form in line_formset
        if form.cleaned_data and not form.cleaned_data.get("DELETE")
    ]


def _build_invoice_payload(
    header_form: InvoiceHeaderForm,
    line_formset: InvoiceLineFormSet,
) -> dict[str, Any]:
    header = header_form.cleaned_data
    lines = _get_active_invoice_lines(line_formset)

    return {
        "customer_id": header["customer_id"],
        "date": header["date"].isoformat(),
        "currency": header["currency"],
        "status": header["status"],
        "line_items": [
            {
                "label": line["label"],
                "unit_price": float(line["unit_price"]),
                "quantity": float(line["quantity"]),
                "vat_rate": float(line["vat_rate"]),
            }
            for line in lines
        ],
    }


@require_http_methods(["GET"])
def home(request: HttpRequest) -> HttpResponse:
    return render(request, "creation_app/home.html")


@require_http_methods(["GET", "POST"])
def set_token(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = TokenForm(request.POST)
        if form.is_valid():
            request.session[SESSION_TOKEN_KEY] = form.cleaned_data["token"]
            messages.success(request, "Token enregistré en session ✅")
            return redirect("creation_app:home")
    else:
        form = TokenForm(initial={"token": _get_session_token(request) or ""})

    return render(request, "creation_app/set_token.html", {"form": form})


@require_http_methods(["GET", "POST"])
def create_customer_view(request: HttpRequest) -> HttpResponse:
    token = _require_session_token(request)
    if not token:
        return redirect("creation_app:set_token")

    form = CustomerForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        payload = _build_customer_payload(form)

        try:
            result = create_customer(payload, token)
            messages.success(request, "Client créé ✅")
            return render(
                request,
                "creation_app/customers.html",
                {"form": form, "result": result},
            )
        except Exception as exc:  # idéalement remplacer par une exception métier dédiée
            _handle_service_error(request, "Création du client", exc)

    return render(request, "creation_app/customers.html", {"form": form})


@require_http_methods(["GET", "POST"])
def create_product_view(request: HttpRequest) -> HttpResponse:
    token = _require_session_token(request)
    if not token:
        return redirect("creation_app:set_token")

    form = ProductForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        payload = _build_product_payload(form)

        try:
            result = create_product(payload, token)
            messages.success(request, "Produit créé ✅")
            return render(
                request,
                "creation_app/products.html",
                {"form": form, "result": result},
            )
        except Exception as exc:  # idéalement remplacer par une exception métier dédiée
            _handle_service_error(request, "Création du produit", exc)

    return render(request, "creation_app/products.html", {"form": form})


@require_http_methods(["GET", "POST"])
def create_invoice_view(request: HttpRequest) -> HttpResponse:
    token = _require_session_token(request)
    if not token:
        return redirect("creation_app:set_token")

    header_form = InvoiceHeaderForm(request.POST or None)
    line_formset = InvoiceLineFormSet(request.POST or None)

    if request.method == "POST" and header_form.is_valid() and line_formset.is_valid():
        lines = _get_active_invoice_lines(line_formset)

        if not lines:
            messages.error(request, "Veuillez ajouter au moins une ligne de facture.")
        else:
            payload = _build_invoice_payload(header_form, line_formset)

            try:
                result = create_invoice(payload, token)
                messages.success(request, "Facture créée ✅")
                return render(
                    request,
                    "creation_app/invoices.html",
                    {
                        "header_form": header_form,
                        "line_formset": line_formset,
                        "result": result,
                    },
                )
            except Exception as exc:  # idéalement remplacer par une exception métier dédiée
                _handle_service_error(request, "Création de la facture", exc)

    return render(
        request,
        "creation_app/invoices.html",
        {
            "header_form": header_form,
            "line_formset": line_formset,
        },
    )