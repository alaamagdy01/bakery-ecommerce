from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'phone_number', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Allergies, delivery instructions...'}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        digits = phone.replace('+', '').replace(' ', '').replace('-', '')
        if not digits.isdigit() or len(digits) < 7:
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
