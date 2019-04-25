from django import forms
from ckeditor.widgets import CKEditorWidget


LEVEL_CHOICES = [
    ('Facile', 'Facile'),
    ('Moyen', 'Moyen'),
    ('Difficile', 'Difficile')
]


class PostCourseForm(forms.Form):
    name = forms.CharField(
        required=True,
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Titre'
            }
        )
    )
    description = forms.CharField(
        required=True,
        widget=CKEditorWidget()
    )
    video_url = forms.URLField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Lien de la vidéo'
            }
        )
    )
    is_free = forms.BooleanField(
        required=False
    )
    price = forms.DecimalField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Prix en MAD'
            }
        )
    )
    duration = forms.CharField(
        required=True,
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Durée'
            }
        )
    )
    image = forms.ImageField(
        required=True,
        widget=forms.FileInput(
            attrs={
                'onchange': 'readURL(this);',
                'class': 'form-control'
            }
        )
    )
    language = forms.CharField(
        required=True,
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Langue du cours'
            }
        )
    )
    level = forms.ChoiceField(
        choices=LEVEL_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'placeholder': 'Niveau du cours',
            }
        )
    )
    has_certificate = forms.BooleanField(
        required=False
    )
    welcome_msg = forms.CharField(
        required=True,
        widget=CKEditorWidget()
    )
    congratulation_msg = forms.CharField(
        required=True,
        widget=CKEditorWidget()
    )


class SendMessageForm(forms.Form):
    object = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'object'
            }
        )
    )
    message = forms.CharField(
        required=True,
        widget=CKEditorWidget()
    )


class ReplyMessageForm(forms.Form):
    message = forms.CharField(
        required=True,
        widget=CKEditorWidget()
    )


class UpdateTeacherProfil(forms.Form):
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            }
        )
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }
        )
    )
    email = forms.CharField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }
        )
    )
    tel = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Téléphone'
            }
        )
    )
    photo_profil = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'onchange': 'readURL(this);'
            }
        )
    )
    facebook = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Facebook'
            }
        )
    )
    youtube = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'YouTube'
            }
        )
    )
    linkedin = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Linkedin'
            }
        )
    )
    twitter = forms.URLField(
        required=False,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Twitter'
            }
        )
    )
    title = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Titre'
            }
        )
    )
    biography = forms.CharField(
        required=False,
        widget=CKEditorWidget()
    )
    cv = forms.FileField(
        required=False
    )


class AddPartForm(forms.Form):
    number = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'id': 'number_part',
                'placeholder': 'Numéro'
            }
        )
    )
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'name_part',
                'placeholder': 'Nom'
            }
        )
    )
    is_free = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'id': 'is_free'
            }
        )
    )


class AddQuizForm(forms.Form):
    title = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Titre'
            }
        )
    )
    description = forms.CharField(
            required=False,
            widget=CKEditorWidget()
    )


class AddQuestionForm(forms.Form):
    text = forms.CharField(
        required=True,
        widget=CKEditorWidget()
    )
    explanation = forms.CharField(
        required=False,
        widget=CKEditorWidget()
    )
    is_multiple = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'id': 'is_multiple'
            }
        )
    )
