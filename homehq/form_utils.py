def style_form(form):
    """Apply dark theme CSS classes to all form widgets."""
    INPUT_TYPES = ('TextInput', 'NumberInput', 'DateInput', 'EmailInput', 
                   'URLInput', 'PasswordInput', 'Textarea', 'Select',
                   'ClearableFileInput')
    for field in form.fields.values():
        wname = field.widget.__class__.__name__
        attrs = field.widget.attrs
        if wname in INPUT_TYPES:
            attrs['class'] = (attrs.get('class', '') + ' form-control-hq').strip()
        elif wname == 'CheckboxInput':
            attrs['class'] = (attrs.get('class', '') + ' form-check-input').strip()
    return form
