from django import forms
from .models import Vehicle, ServiceLog

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


class VehicleForm(DarkFormMixin, forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['year', 'make', 'model', 'color', 'vin', 'plate', 'odometer', 'insurance_policy', 'title_scan', 'registration_scan', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class ServiceLogForm(DarkFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceLog
        fields = ['service_type', 'date', 'odometer_at_service', 'next_service_odometer', 'cost', 'shop', 'receipt_scan', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
