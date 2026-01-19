"""
services.py
Ce module constitue la couche de services pour l'API Pennylane.
Il encapsule les appels HTTP externes et fournit des fonctions
réutilisables pour créer des clients, des factures, des produits
et rechercher des entités. On y gère également la construction des entêtes
d'authentification et la gestion des erreurs.
"""

import requests
from django.conf import settings

# Entêtes par défaut utilisant le jeton stocké dans les paramètres.
HEADERS = {
    'Authorization': f"Bearer {getattr(settings, 'PENNYLANE_API_TOKEN', '')}",
    'Content-Type': 'application/json',
}
BASE_URL = getattr(settings, 'PENNYLANE_API_BASE_URL', 'https://app.pennylane.com/api/external/v2')


def handle_response(response):
    """
    Centralise la gestion des réponses HTTP.
    Si le statut est inférieur à 400, retourne le JSON du serveur.
    Sinon, lève une exception avec le message d'erreur.
    """
    if response.status_code < 400:
        return response.json()
    try:
        message = response.json().get('message', response.text)
    except Exception:
        message = response.text
    raise Exception(f"Erreur {response.status_code}: {message}")


def get_headers(token=None):
    """
    Construit les entêtes pour la requête.
    Si un token est fourni, il remplace celui des settings.
    """
    headers = HEADERS.copy()
    if token:
        headers['Authorization'] = f'Bearer {token}'
    return headers


def create_customer(data, token=None):
    """
    Envoie une requête POST à /company_customers pour créer un nouveau client.
    `data` doit contenir les clés: name, email, address, postal_code, city, country.
    """
    url = f"{BASE_URL}/company_customers"
    body = {
        "name": data['name'],
        "emails": [data['email']],
        "billing_address": {
            "address": data.get('address'),
            "postal_code": data.get('postal_code'),
            "city": data.get('city'),
            "country": data.get('country') or 'FR',
        },
    }
    response = requests.post(url, json=body, headers=get_headers(token))
    return handle_response(response)


def create_invoice(header_data, lines, token=None):
    """
    Envoie une requête POST à /customer_invoices pour créer une facture.
    `header_data` contient les informations sur la facture (client, date, devise, statut).
    `lines` est une liste de dictionnaires décrivant chaque ligne.
    """
    url = f"{BASE_URL}/customer_invoices"
    body = {
        "customer_id": header_data['customer_id'],
        "date": str(header_data['date']),
        "currency": header_data['currency'],
        "status": header_data['status'],
        "line_items": [
            {
                "label": line['label'],
                "unit_price": float(line['unit_price']),
                "quantity": float(line['quantity']),
                "vat_rate": float(line['vat_rate']),
            }
            for line in lines
        ]
    }
    response = requests.post(url, json=body, headers=get_headers(token))
    return handle_response(response)


def create_product(data, token=None):
    """
    Envoie une requête POST à /products pour créer un produit.
    `data` doit contenir: label, unit_price, vat_rate, currency.
    """
    url = f"{BASE_URL}/products"
    body = {
        "label": data['label'],
        "unit_price": float(data['unit_price']),
        "vat_rate": float(data['vat_rate']),
        "currency": data['currency'],
    }
    response = requests.post(url, json=body, headers=get_headers(token))
    return handle_response(response)


def search_entities(entity_type, query='', token=None):
    """
    Envoie une requête GET pour rechercher des entités.
    `entity_type` détermine la ressource (ex: company_customers).
    Si `query` est non vide, un filtre est ajouté pour la recherche par nom.
    """
    endpoint = f"/{entity_type}"
    if query:
        endpoint += f"?filter=[{{\"field\":\"name\",\"operator\":\"contains\",\"value\":\"{query}\"}}]"
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=get_headers(token))
    return handle_response(response)
