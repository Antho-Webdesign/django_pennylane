"""
services.py
Ce module constitue la couche de services pour l'API Pennylane.
Il encapsule les appels HTTP externes et fournit des fonctions
réutilisables pour créer des clients, des factures, des produits
et rechercher des entités. On y gère également la construction des entêtes
d'authentification et la gestion des erreurs.
"""

from __future__ import annotations

import json
from typing import Any

import requests
from django.conf import settings

BASE_URL = getattr(settings, 'PENNYLANE_API_BASE_URL', 'https://app.pennylane.com/api/external/v2')
REQUEST_TIMEOUT_SECONDS = 20


def handle_response(response: requests.Response) -> dict[str, Any]:
    """
    Centralise la gestion des réponses HTTP.
    Si le statut est inférieur à 400, retourne le JSON du serveur.
    Sinon, lève une exception avec le message d'erreur.
    """
    try:
        payload = response.json()
    except ValueError:
        payload = {'raw': response.text}

    if response.ok:
        return payload if isinstance(payload, dict) else {'data': payload}

    message = payload.get('message') if isinstance(payload, dict) else response.text
    raise RuntimeError(f"Erreur {response.status_code}: {message}")


def get_headers(token: str | None = None) -> dict[str, str]:
    """
    Construit les entêtes pour la requête.
    Si un token est fourni, il remplace celui des settings.
    """
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    auth_token = token or getattr(settings, 'PENNYLANE_API_TOKEN', '')
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'

    return headers


def _request(
    method: str,
    endpoint: str,
    *,
    token: str | None = None,
    payload: dict[str, Any] | None = None,
    params: dict[str, str] | None = None,
) -> dict[str, Any]:
    url = f'{BASE_URL}{endpoint}'
    response = requests.request(
        method,
        url,
        headers=get_headers(token),
        params=params,
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return handle_response(response)


def create_customer(data: dict[str, Any], token: str | None = None) -> dict[str, Any]:
    """
    Envoie une requête POST à /company_customers pour créer un nouveau client.
    `data` doit contenir les clés: name, email, address, postal_code, city, country.
    """
    body = {
        'name': data['name'],
        'emails': [data['email']],
        'billing_address': {
            'address': data.get('address'),
            'postal_code': data.get('postal_code'),
            'city': data.get('city'),
            'country': data.get('country') or 'FR',
        },
    }
    return _request('POST', '/company_customers', token=token, payload=body)


def create_invoice(
    header_data: dict[str, Any],
    lines: list[dict[str, Any]],
    token: str | None = None,
) -> dict[str, Any]:
    """
    Envoie une requête POST à /customer_invoices pour créer une facture.
    `header_data` contient les informations sur la facture (client, date, devise, statut).
    `lines` est une liste de dictionnaires décrivant chaque ligne.
    """
    body = {
        'customer_id': header_data['customer_id'],
        'date': str(header_data['date']),
        'currency': header_data['currency'],
        'status': header_data['status'],
        'line_items': [
            {
                'label': line['label'],
                'unit_price': float(line['unit_price']),
                'quantity': float(line['quantity']),
                'vat_rate': float(line['vat_rate']),
            }
            for line in lines
        ],
    }
    return _request('POST', '/customer_invoices', token=token, payload=body)


def create_product(data: dict[str, Any], token: str | None = None) -> dict[str, Any]:
    """
    Envoie une requête POST à /products pour créer un produit.
    `data` doit contenir: label, unit_price, vat_rate, currency.
    """
    body = {
        'label': data['label'],
        'unit_price': float(data['unit_price']),
        'vat_rate': float(data['vat_rate']),
        'currency': data['currency'],
    }
    return _request('POST', '/products', token=token, payload=body)


def search_entities(entity_type: str, query: str = '', token: str | None = None) -> dict[str, Any]:
    """
    Envoie une requête GET pour rechercher des entités.
    `entity_type` détermine la ressource (ex: company_customers).
    Si `query` est non vide, un filtre est ajouté pour la recherche par nom.
    """
    params = None
    if query:
        params = {
            'filter': json.dumps(
                [{'field': 'name', 'operator': 'contains', 'value': query}],
                separators=(',', ':'),
            )
        }
    return _request('GET', f'/{entity_type}', token=token, params=params)
