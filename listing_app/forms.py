from django import forms

class NameFilterForm(forms.Form):
    q = forms.CharField(
        label="",
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Nom contient…",
            "style": "min-width: 260px;",
        })
    )
