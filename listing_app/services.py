"""
Couche service GET pour Pennylane.
On réutilise le token en session si présent, sinon fallback settings.PENNYLANE_API_TOKEN.
"""

from __future__ import annotations

import json

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


def _get(endpoint: str, *, token: str | None = None, params: dict[str, str] | None = None) -> dict:
    url = f"{settings.PENNYLANE_API_BASE_URL}{endpoint}"
    resp = requests.get(
        url,
        headers=_get_headers(token),
        params=params,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return _handle_response(resp)


def list_entities(entity_type: str, q: str = "", token: str | None = None) -> dict:
    """
    Liste une ressource Pennylane.
    - entity_type: company_customers, products, customer_invoices, supplier_invoices
    - q: filtre optionnel 'name contains' via filter=...
    """
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
    return _get(
        "/trial_balance",
        token=token,
        params={"use_2026_api_changes": "true"},
    )


def get_ledger_accounts(token: str | None = None) -> dict:
    return _get(
        "/ledger_accounts",
        token=token,
        params={"use_2026_api_changes": "true"},
    )
