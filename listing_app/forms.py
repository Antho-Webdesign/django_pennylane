"""
Formulaire de filtrage simple par nom (contains).
On ne fait que du GET => on utilisera request.GET dans les vues.
"""

from django import forms


class NameFilterForm(forms.Form):
    q = forms.CharField(
        label="Recherche (nom contient)",
        required=False,
        max_length=255,
    )

    def clean_q(self):
        """Nettoie le champ de recherche en supprimant les espaces superflus."""
        q = self.cleaned_data.get("q", "")
        return q.strip()


