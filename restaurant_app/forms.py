import re
from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name", "customer_phone", "table_number"]
        widgets = {
            "customer_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your full name",
                    "required": True,
                    "maxlength": 100,
                    "id": "customer_name",
                }
            ),
            "customer_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter 10-digit mobile number",
                    "required": True,
                    "maxlength": 15,
                    "id": "customer_phone",
                }
            ),
            "table_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Table 4 / Takeaway",
                    "maxlength": 20,
                    "id": "table_number",
                }
            ),
        }

    def clean_customer_phone(self):
        phone = self.cleaned_data.get("customer_phone", "").strip()
        cleaned_phone = re.sub(r"[^\d+]", "", phone)
        if len(cleaned_phone) < 10:
            raise forms.ValidationError("Please enter a valid phone number with at least 10 digits.")
        return phone

    def clean_customer_name(self):
        name = self.cleaned_data.get("customer_name", "").strip()
        if len(name) < 2:
            raise forms.ValidationError("Customer name must be at least 2 characters long.")
        return name


class OrderStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(
        choices=Order.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )
