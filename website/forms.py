# project/apps/website/forms.py
from django import forms

class ContactForm(forms.Form):
    # Campos del formulario clásico
    name = forms.CharField(max_length=120)
    email = forms.EmailField()
    phone = forms.CharField(max_length=50, required=False)
    company = forms.CharField(max_length=120, required=False)
    message = forms.CharField(widget=forms.Textarea)

    # Selects opcionales (permitimos vacío)
    project_type = forms.CharField(max_length=60, required=False)
    sector = forms.CharField(max_length=60, required=False)
    timeline = forms.CharField(max_length=20, required=False)

    # Campos del chat (hidden en tu plantilla)
    transcript = forms.CharField(required=False)
    pains_json = forms.CharField(required=False)
    budget = forms.CharField(required=False)
    brief = forms.CharField(required=False)

    # Honeypot anti-spam (no mostrar al usuario real)
    website = forms.CharField(required=False)

    def clean_website(self):
        # Si viene con valor => bot
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detectado.")
        return ""
