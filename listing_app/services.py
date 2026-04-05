"""
Couche service GET/POST/PUT pour Pennylane.
On réutilise le token en session si présent, sinon fallback settings.PENNYLANE_API_TOKEN.
"""

from __future__ import annotations

import json
from typing import Any

import requests
from django.conf import settings

REQUEST_TIMEOUT_SECONDS = 20


def _get_headers(token: str | None) -> dict[str, str]:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    auth_token = token or getattr(settings, "PENNYLANE_API_TOKEN", "")
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    return headers


def _handle_response(resp: requests.Response) -> dict:
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}

    if resp.ok:
        return data

    message = data.get("message") if isinstance(data, dict) else None
    raise RuntimeError(f"Pennylane HTTP {resp.status_code}: {message or resp.text}")


def _request(
    method: str,
    endpoint: str,
    *,
    token: str | None = None,
    params: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
) -> dict:
    url = f"{settings.PENNYLANE_API_BASE_URL}{endpoint}"
    resp = requests.request(
        method,
        url,
        headers=_get_headers(token),
        params=params,
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return _handle_response(resp)


def _get(endpoint: str, *, token: str | None = None, params: dict[str, str] | None = None) -> dict:
    return _request("GET", endpoint, token=token, params=params)


# ----------------------------
# Existing listing methods
# ----------------------------

def list_entities(entity_type: str, q: str = "", token: str | None = None) -> dict:
    params = None
    if q:
        params = {
            "filter": json.dumps(
                [{"field": "name", "operator": "contains", "value": q}],
                separators=(",", ":"),
            )
        }
    return _get(f"/{entity_type}", token=token, params=params)


def list_customers(token: str | None = None) -> dict:
    return _get("/customers", token=token, params={"sort": "-id"})


def list_products(token: str | None = None) -> dict:
    return _get("/products", token=token, params={"sort": "-id"})


def list_customer_invoices(token: str | None = None) -> dict:
    return _get("/customer_invoices", token=token, params={"sort": "-id"})


def get_trial_balance(token: str | None = None) -> dict:
    return _get("/trial_balance", token=token, params={"use_2026_api_changes": "true"})


def get_ledger_accounts(token: str | None = None) -> dict:
    return _get("/ledger_accounts", token=token, params={"use_2026_api_changes": "true"})


# ----------------------------
# Accounting
# ----------------------------

def list_journals(token: str | None = None) -> dict:
    return _get("/journals", token=token)


def list_ledger_attachments(token: str | None = None) -> dict:
    return _get("/ledger_attachments", token=token)


def list_ledger_entries(token: str | None = None) -> dict:
    return _get("/ledger_entries", token=token)


def list_ledger_entry_lines(token: str | None = None) -> dict:
    return _get("/ledger_entry_lines", token=token)


def list_fiscal_years(token: str | None = None) -> dict:
    return _get("/fiscal_years", token=token)


def list_accounting_exports(token: str | None = None) -> dict:
    return _get("/accounting_exports", token=token)


def list_exports(token: str | None = None) -> dict:
    return _get("/exports", token=token)


# ----------------------------
# Analytics
# ----------------------------

def list_category_groups(token: str | None = None) -> dict:
    return _get("/category_groups", token=token)


def list_categories(token: str | None = None) -> dict:
    return _get("/categories", token=token)


# ----------------------------
# Billing subscriptions
# ----------------------------

def list_billing_subscriptions(token: str | None = None) -> dict:
    return _get("/billing_subscriptions", token=token)


# ----------------------------
# Changelogs
# ----------------------------

def list_changelogs(token: str | None = None) -> dict:
    return _get("/changelogs", token=token)


# ----------------------------
# Commercial documents
# ----------------------------

def list_commercial_documents(token: str | None = None) -> dict:
    return _get("/commercial_documents", token=token)


# ----------------------------
# Customer invoices + related
# ----------------------------

def list_customer_invoice_templates(token: str | None = None) -> dict:
    return _get("/customer_invoice_templates", token=token)


def retrieve_customer_invoice(invoice_id: str, token: str | None = None) -> dict:
    return _get(f"/customer_invoices/{invoice_id}", token=token)


def create_company_customer(payload: dict[str, Any], token: str | None = None) -> dict:
    """
    Crée un client société via /company_customers.
    Le payload suit le format Pennylane (ledger_account, billing_address, etc.).
    """
    return _request("POST", "/company_customers", token=token, payload=payload)


# ----------------------------
# E-invoices / file attachments / mandates / quotes
# ----------------------------

def list_e_invoices(token: str | None = None) -> dict:
    return _get("/e_invoices", token=token)


def list_file_attachments(token: str | None = None) -> dict:
    return _get("/file_attachments", token=token)


def list_mandates(token: str | None = None) -> dict:
    return _get("/mandates", token=token)


def list_quotes(token: str | None = None) -> dict:
    return _get("/quotes", token=token)


def retrieve_quote(quote_id: str, token: str | None = None) -> dict:
    return _get(f"/quotes/{quote_id}", token=token)


# ----------------------------
# Supplier invoices
# ----------------------------

def list_supplier_invoices(token: str | None = None) -> dict:
    return _get("/supplier_invoices", token=token)


def retrieve_supplier_invoice(invoice_id: str, token: str | None = None) -> dict:
    return _get(f"/supplier_invoices/{invoice_id}", token=token)


def list_supplier_invoice_lines(invoice_id: str, token: str | None = None) -> dict:
    return _get(f"/supplier_invoices/{invoice_id}/invoice_lines", token=token)


def list_supplier_invoice_categories(invoice_id: str, token: str | None = None) -> dict:
    return _get(f"/supplier_invoices/{invoice_id}/categories", token=token)


def list_supplier_invoice_payments(invoice_id: str, token: str | None = None) -> dict:
    return _get(f"/supplier_invoices/{invoice_id}/payments", token=token)


def list_supplier_invoice_matched_transactions(invoice_id: str, token: str | None = None) -> dict:
    return _get(f"/supplier_invoices/{invoice_id}/matched_transactions", token=token)


def import_supplier_invoice(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/supplier_invoices/import", token=token, payload=payload)


def link_purchase_request_to_supplier_invoice(
    invoice_id: str,
    payload: dict[str, Any],
    token: str | None = None,
) -> dict:
    return _request(
        "POST",
        f"/supplier_invoices/{invoice_id}/link_purchase_request",
        token=token,
        payload=payload,
    )


def import_supplier_e_invoice(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/supplier_invoices/import_e_invoice", token=token, payload=payload)


def update_supplier_invoice(
    invoice_id: str,
    payload: dict[str, Any],
    token: str | None = None,
) -> dict:
    return _request("PUT", f"/supplier_invoices/{invoice_id}", token=token, payload=payload)


def categorize_supplier_invoice(
    invoice_id: str,
    payload: dict[str, Any],
    token: str | None = None,
) -> dict:
    return _request(
        "PUT",
        f"/supplier_invoices/{invoice_id}/categorize",
        token=token,
        payload=payload,
    )


def update_supplier_invoice_payment_status(
    invoice_id: str,
    payload: dict[str, Any],
    token: str | None = None,
) -> dict:
    return _request(
        "PUT",
        f"/supplier_invoices/{invoice_id}/payment_status",
        token=token,
        payload=payload,
    )


def validate_supplier_invoice_accounting(invoice_id: str, token: str | None = None) -> dict:
    return _request("PUT", f"/supplier_invoices/{invoice_id}/validate_accounting", token=token)


# ----------------------------
# Purchase requests / suppliers
# ----------------------------

def list_purchase_requests(token: str | None = None) -> dict:
    return _get("/purchase_requests", token=token)


def list_suppliers(token: str | None = None) -> dict:
    return _get("/suppliers", token=token)


# ----------------------------
# Transactions
# ----------------------------

def list_bank_accounts(token: str | None = None) -> dict:
    return _get("/bank_accounts", token=token)


def list_transactions(token: str | None = None) -> dict:
    return _get("/transactions", token=token)


# ----------------------------
# Users
# ----------------------------

def list_users(token: str | None = None) -> dict:
    return _get("/users", token=token)
