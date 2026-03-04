from django import forms
from .models import Asset, InsurancePolicy

class DarkFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        INPUT_TYPES = ('TextInput', 'NumberInput', 'DateInput', 'EmailInput',
                       'URLInput', 'PasswordInput', 'Textarea', 'Select',
                       'ClearableFileInput', 'SelectMultiple')
        for field in self.fields.values():
            wname = field.widget.__class__.__name__
            attrs = field.widget.attrs
            if wname in INPUT_TYPES:
                attrs['class'] = (attrs.get('class', '') + ' form-control-hq').strip()
            elif wname == 'CheckboxInput':
                attrs['class'] = (attrs.get('class', '') + ' form-check-input').strip()


class AssetForm(DarkFormMixin, forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'category', 'value', 'serial_number', 'purchase_date', 'purchase_price', 'insurance_policy', 'receipt_image', 'manual', 'notes']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class InsurancePolicyForm(DarkFormMixin, forms.ModelForm):
    class Meta:
        model = InsurancePolicy
        fields = ['name', 'provider', 'policy_number', 'coverage_amount', 'expiry_date', 'notes']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
