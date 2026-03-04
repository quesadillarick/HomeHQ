from django import forms
from .models import Note, NoteCategory

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


class NoteForm(DarkFormMixin, forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'body', 'category', 'tags']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 15, 'class': 'font-monospace'}),
            'tags': forms.TextInput(attrs={'placeholder': '#Emergency, #PaintCodes'}),
        }
