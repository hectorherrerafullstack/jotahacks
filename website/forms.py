# project/apps/website/forms.py
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, required=True)
    phone = forms.CharField(max_length=50, required=True)  # ← ahora True
    company = forms.CharField(max_length=120, required=False)
    message = forms.CharField(widget=forms.Textarea, required=True)

    project_type = forms.CharField(max_length=60, required=False)
    sector = forms.CharField(max_length=60, required=True)

    timeline = forms.CharField(max_length=20, required=False)

    transcript = forms.CharField(required=False)
    pains_json = forms.CharField(required=False)
    budget = forms.CharField(required=False)
    brief = forms.CharField(required=False)

    # Honeypot anti-spam
    website = forms.CharField(required=False)
    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detectado.")
        return ""
