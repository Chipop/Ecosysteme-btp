from django import forms


class ImportFile(forms.Form):
    upload_cv = forms.FileField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'uploadButton-input',
                'accept': 'image/*, application/pdf, application/doc'
            }
        )
    )
