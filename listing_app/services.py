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


def create_journal(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/journals", token=token, payload=payload)


def list_ledger_attachments(token: str | None = None) -> dict:
    return _get("/ledger_attachments", token=token)


def create_ledger_attachment(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/ledger_attachments", token=token, payload=payload)


def list_ledger_entries(token: str | None = None) -> dict:
    return _get("/ledger_entries", token=token)


def create_ledger_entry(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/ledger_entries", token=token, payload=payload)


def list_ledger_entry_lines(token: str | None = None) -> dict:
    return _get("/ledger_entry_lines", token=token)


def create_ledger_entry_line(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/ledger_entry_lines", token=token, payload=payload)


def list_fiscal_years(token: str | None = None) -> dict:
    return _get("/fiscal_years", token=token)


def list_accounting_exports(token: str | None = None) -> dict:
    return _get("/accounting_exports", token=token)


def create_accounting_export(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/accounting_exports", token=token, payload=payload)


def list_exports(token: str | None = None) -> dict:
    return _get("/exports", token=token)


def create_export(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/exports", token=token, payload=payload)


# ----------------------------
# Analytics
# ----------------------------

def list_category_groups(token: str | None = None) -> dict:
    return _get("/category_groups", token=token)


def create_category_group(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/category_groups", token=token, payload=payload)


def list_categories(token: str | None = None) -> dict:
    return _get("/categories", token=token)


def create_category(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/categories", token=token, payload=payload)


# ----------------------------
# Billing subscriptions
# ----------------------------

def list_billing_subscriptions(token: str | None = None) -> dict:
    return _get("/billing_subscriptions", token=token)


def create_billing_subscription(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/billing_subscriptions", token=token, payload=payload)


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


def create_commercial_document(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/commercial_documents", token=token, payload=payload)


# ----------------------------
# Customer invoices + related
# ----------------------------

def list_customer_invoice_templates(token: str | None = None) -> dict:
    return _get("/customer_invoice_templates", token=token)


def create_customer_invoice_template(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/customer_invoice_templates", token=token, payload=payload)


def list_customer_invoices_all(token: str | None = None) -> dict:
    return _get("/customer_invoices", token=token)


def retrieve_customer_invoice(invoice_id: str, token: str | None = None) -> dict:
    return _get(f"/customer_invoices/{invoice_id}", token=token)


def create_customer_invoice(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/customer_invoices", token=token, payload=payload)


def list_customers_all(token: str | None = None) -> dict:
    return _get("/customers", token=token)


def retrieve_customer(customer_id: str, token: str | None = None) -> dict:
    return _get(f"/customers/{customer_id}", token=token)


def retrieve_company_customer(customer_id: str, token: str | None = None) -> dict:
    return _get(f"/company_customers/{customer_id}", token=token)


def retrieve_individual_customer(customer_id: str, token: str | None = None) -> dict:
    return _get(f"/individual_customers/{customer_id}", token=token)


def list_customer_contacts(customer_id: str, token: str | None = None) -> dict:
    return _get(f"/customers/{customer_id}/contacts", token=token)


def list_customer_categories(customer_id: str, token: str | None = None) -> dict:
    return _get(f"/customers/{customer_id}/categories", token=token)


def create_company_customer(payload: dict[str, Any], token: str | None = None) -> dict:
    """
    Crée un client société via /company_customers.
    Le payload suit le format Pennylane (ledger_account, billing_address, etc.).
    """
    return _request("POST", "/company_customers", token=token, payload=payload)


def create_individual_customer(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/individual_customers", token=token, payload=payload)


# ----------------------------
# E-invoices / file attachments / mandates / quotes
# ----------------------------

def list_e_invoices(token: str | None = None) -> dict:
    return _get("/e_invoices", token=token)


def create_e_invoice(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/e_invoices", token=token, payload=payload)


def list_file_attachments(token: str | None = None) -> dict:
    return _get("/file_attachments", token=token)


def create_file_attachment(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/file_attachments", token=token, payload=payload)


def list_mandates(token: str | None = None) -> dict:
    return _get("/mandates", token=token)


def create_mandate(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/mandates", token=token, payload=payload)


def list_quotes(token: str | None = None) -> dict:
    return _get("/quotes", token=token)


def create_quote(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/quotes", token=token, payload=payload)


def retrieve_quote(quote_id: str, token: str | None = None) -> dict:
    return _get(f"/quotes/{quote_id}", token=token)


# ----------------------------
# Supplier invoices
# ----------------------------

def list_supplier_invoices(token: str | None = None) -> dict:
    return _get("/supplier_invoices", token=token)


def create_supplier_invoice(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/supplier_invoices", token=token, payload=payload)


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


def create_purchase_request(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/purchase_requests", token=token, payload=payload)


def list_suppliers(token: str | None = None) -> dict:
    return _get("/suppliers", token=token)


def create_supplier(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/suppliers", token=token, payload=payload)


# ----------------------------
# Transactions
# ----------------------------

def list_bank_accounts(token: str | None = None) -> dict:
    return _get("/bank_accounts", token=token)


def create_bank_account(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/bank_accounts", token=token, payload=payload)


def list_transactions(token: str | None = None) -> dict:
    return _get("/transactions", token=token)


def create_transaction(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/transactions", token=token, payload=payload)


# ----------------------------
# Users
# ----------------------------

def list_users(token: str | None = None) -> dict:
    return _get("/users", token=token)


def create_user(payload: dict[str, Any], token: str | None = None) -> dict:
    return _request("POST", "/users", token=token, payload=payload)
