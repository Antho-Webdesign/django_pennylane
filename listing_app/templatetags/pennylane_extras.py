import json
from django import template

register = template.Library()


@register.filter
def pretty_json(value) -> str:
    """
    Transforme un dict/list Python en JSON indenté lisible.
    Si value est déjà une string => renvoie tel quel.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value)


@register.filter
def get_first_list(result):
    """
    Beaucoup d'APIs renvoient un dict contenant une liste sous une clé.
    Ex: {"company_customers": [...]} ou {"products": [...]} etc.
    - Si result est une liste => renvoie result
    - Si dict => renvoie la première valeur qui est une liste
    - Sinon => None
    """
    if result is None:
        return None
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        for v in result.values():
            if isinstance(v, list):
                return v
    return None


@register.filter
def dict_get(d, key):
    """Accède à d[key] en template sans crash."""
    if isinstance(d, dict):
        return d.get(key)
    return None
