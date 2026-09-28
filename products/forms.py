from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """Used by admin/staff to add or edit a bakery product (FR-2)."""

    class Meta:
        model = Product
        fields = [
            'category', 'name', 'slug', 'description', 'ingredients',
            'price', 'stock', 'image', 'is_available', 'is_featured',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data['stock']
        if stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock


class ProductSearchForm(forms.Form):
    """FR-3: search and filter products."""
    q = forms.CharField(required=False, label='Search')
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), required=False, empty_label="All categories"
    )
    min_price = forms.DecimalField(required=False, min_value=0)
    max_price = forms.DecimalField(required=False, min_value=0)
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Newest'),
            ('price_asc', 'Price: Low to High'),
            ('price_desc', 'Price: High to Low'),
            ('name', 'Name: A-Z'),
        ],
    )
