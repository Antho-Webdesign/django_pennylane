"""
Couche de service Pennylane : encapsule les appels HTTP.
- _get_headers : construit l’Authorization Bearer
- create_customer / create_product / create_invoice : POST
"""

from __future__ import annotations
import requests
from django.conf import settings


def _get_headers(token: str | None) -> dict[str, str]:
    """
    Construit les headers.
    Si token est None, on fallback sur settings.PENNYLANE_API_TOKEN (optionnel).
    """
    headers = {"Content-Type": "application/json"}
    auth_token = token or getattr(settings, "PENNYLANE_API_TOKEN", "")
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    return headers


def _handle_response(resp: requests.Response) -> dict:
    """
    Centralise la gestion d’erreurs.
    - Si 2xx/3xx => retourne JSON
    - Sinon => lève une exception avec détails
    """
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}

    if resp.ok:
        return data

    message = data.get("message") if isinstance(data, dict) else None
    raise RuntimeError(f"Pennylane HTTP {resp.status_code}: {message or resp.text}")


def create_customer(payload: dict, token: str | None) -> dict:
    url = f"{settings.PENNYLANE_API_BASE_URL}/company_customers"
    resp = requests.post(url, json=payload, headers=_get_headers(token), timeout=20)
    return _handle_response(resp)


def create_product(payload: dict, token: str | None) -> dict:
    url = f"{settings.PENNYLANE_API_BASE_URL}/products"
    resp = requests.post(url, json=payload, headers=_get_headers(token), timeout=20)
    return _handle_response(resp)


def create_invoice(payload: dict, token: str | None) -> dict:
    # ⚠️ endpoint Pennylane v2 : customer_invoices (comme dans ton React)
    url = f"{settings.PENNYLANE_API_BASE_URL}/customer_invoices"
    resp = requests.post(url, json=payload, headers=_get_headers(token), timeout=20)
    return _handle_response(resp)
