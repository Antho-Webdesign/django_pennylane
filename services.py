# services.py
import requests
from django.conf import settings

API_BASE_URL = 'https://app.pennylane.com/api/external/v2'

# Utilitaire pour construire l’entête d’autorisation
def _get_headers(token: str | None = None) -> dict[str, str]:
    headers = {
        'Content-Type': 'application/json',
    }
    # utilise le jeton passé en paramètre ou celui stocké dans settings
    auth_token = token if token else getattr(settings, 'PENNYLANE_API_TOKEN', '')
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    return headers

# Création d’un client
def create_customer(data: dict, token: str | None = None) -> tuple[bool, dict | str]:
    url = f"{API_BASE_URL}/company_customers"
    headers = _get_headers(token)
    payload = {
        'name': data['name'],
        'emails': [data['email']],
        'billing_address': {
            'address': data.get('address', ''),
            'postal_code': data.get('postal_code', ''),
            'city': data.get('city', ''),
            'country': data.get('country', 'FR'),
        },
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.ok, response.json() if response.ok else response.text

# Création d’une facture
def create_invoice(header_data: dict, line_items: list[dict], token: str | None = None) -> tuple[bool, dict | str]:
    url = f"{API_BASE_URL}/invoices"
    headers = _get_headers(token)
    payload = {
        'customer_id': header_data['customer_id'],
        'date': header_data['date'].isoformat(),
        'currency': header_data['currency'],
        'status': header_data['status'],
        'lines': [
            {
                'label': item['label'],
                'unit_price': float(item['unit_price']),
                'quantity': float(item['quantity']),
                'vat_rate': float(item['vat_rate']),
            } for item in line_items
        ],
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.ok, response.json() if response.ok else response.text

# Création d’un produit
def create_product(data: dict, token: str | None = None) -> tuple[bool, dict | str]:
    url = f"{API_BASE_URL}/products"
    headers = _get_headers(token)
    payload = {
        'label': data['label'],
        'unit_price': float(data['unit_price']),
        'vat_rate': float(data['vat_rate']),
        'currency': data['currency'],
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.ok, response.json() if response.ok else response.text

# Recherche d’entités
def search_entities(entity_type: str, query: str = '', token: str | None = None) -> tuple[bool, dict | str]:
    url = f"{API_BASE_URL}/{entity_type}"
    headers = _get_headers(token)
    params = {'search': query} if query else {}
    response = requests.get(url, headers=headers, params=params)
    return response.ok, response.json() if response.ok else response.text
