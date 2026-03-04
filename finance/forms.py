from django import forms
from .models import Bill, Budget, BudgetExpense, CalendarEvent, BillPayment


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


class BillForm(DarkFormMixin, forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['name', 'amount', 'frequency', 'due_date', 'url', 'is_active', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes':    forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'due_date': 'Sets the day-of-month for recurring bills and the start month.',
            'url':      'Link to the payment portal or biller website.',
            'is_active':'Uncheck to stop appearing in future months.',
        }


class BudgetForm(DarkFormMixin, forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'limit', 'month', 'year']
        widgets = {
            'month': forms.NumberInput(attrs={'min': 1, 'max': 12}),
            'year':  forms.NumberInput(attrs={'min': 2020, 'max': 2100}),
        }


class BudgetExpenseForm(DarkFormMixin, forms.ModelForm):
    class Meta:
        model = BudgetExpense
        fields = ['description', 'amount', 'date']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}


class CalendarEventForm(DarkFormMixin, forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ['title', 'date', 'end_date', 'frequency', 'repeat_until', 'color', 'notes']
        widgets = {
            'date':         forms.DateInput(attrs={'type': 'date'}),
            'end_date':     forms.DateInput(attrs={'type': 'date'}),
            'repeat_until': forms.DateInput(attrs={'type': 'date'}),
            'notes':        forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'end_date':     'For single multi-day events (ignored when repeating).',
            'repeat_until': 'Stop generating occurrences after this date. Leave blank for indefinite.',
        }
