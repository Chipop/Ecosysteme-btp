from django import forms
from ckeditor.widgets import CKEditorWidget


class AnswerForm(forms.Form):
    content = forms.CharField(
        widget=CKEditorWidget()
    )


class AddQuestionForm(forms.Form):
    title = forms.CharField(
        max_length=155,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Comment améliorer le...',
                'autocomplete': 'off',
            }
        )
    )

    tags = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'data-role': 'tagsinput'
            }
        )
    )

    content = forms.CharField(
        required=False,
        widget=CKEditorWidget()
    )


class AddPostForm(forms.Form):
    title = forms.CharField(
        max_length=155,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Le BTP entre...',
                'autocomplete': 'off',
            }
        )
    )

    tags = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'data-role': 'tagsinput'
            }
        )
    )

    content = forms.CharField(
        required=False,
        widget=CKEditorWidget()
    )

    image = forms.ImageField(
        required=False
    )


FONCTION_CHOICES = [
        ('Autre', 'Autre'),
        ('Agent de service public', 'Agent de service public'),
        ('Architecte', 'Architecte'),
        ('Artisan', 'Artisan'),
        ('Chef de projet', 'Chef de projet'),
        ('Commerçant', 'Commerçant'),
        ('Consultant', 'Consultant'),
        ('Directeur - Chef de service', 'Directeur - Chef de service'),
        ('Direction générale(PDG, DG, Gérant)', 'Direction générale(PDG, DG, Gérant)'),
        ('Elu local, Conseiller municipaux', 'Elu local, Conseiller municipaux'),
        ('Elu territorial, Conseiller Général / Conseil Régional', 'Elu territorial, Conseiller Général / Conseil Régional'),
        ('Enseignant chercheur', 'Enseignant chercheur'),
        ('Etudiant', 'Etudiant'),
        ('Haut fonctionnaire(Etat / Ministères)', 'Haut fonctionnaire(Etat / Ministères)'),
        ('Ingénieur', 'Ingénieur'),
        ('Président, Vice - Président', 'Président, Vice - Président'),
        ('Responsable - Chargé - Attaché', 'Responsable - Chargé - Attaché'),
        ('Technicien', 'Technicien'),
        ('Urbaniste - Paysagiste', 'Urbaniste - Paysagiste'),
    ]


class UpdateProfileForm(forms.Form):
    first_name = forms.CharField(
        max_length=155,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Entrez votre prénom'
            }
        )
    )
    last_name = forms.CharField(
        max_length=155,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Entrez votre nom'
            }
        )
    )
    description = forms.CharField(
        max_length=300,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 5
            }
        )
    )
    facebook = forms.URLField(
        required=False,
        max_length=300,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Lien Facebook'
            }
        )
    )
    twitter = forms.URLField(
        required=False,
        max_length=300,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Lien Twitter'
            }
        )
    )
    instagram = forms.URLField(
        required=False,
        max_length=300,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Lien Instagram'
            }
        )
    )
    youtube = forms.URLField(
        required=False,
        max_length=300,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Lien Youtube'
            }
        )
    )
    linkedIn = forms.URLField(
        required=False,
        max_length=300,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Lien LinkedIn'
            }
        )
    )
    job = forms.ChoiceField(
        choices=FONCTION_CHOICES,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        )
    )


class UpdatePImageForm(forms.Form):
    image_profile = forms.ImageField()


class UpdateCImageForm(forms.Form):
    image_cover = forms.ImageField()


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=60,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Entrez votre nom complet'
            }
        )
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Entrez votre mail'
            }
        )
    )

    subject = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Entrez l\'objet de votre message'
            }
        )
    )

    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 10,
                'cols': 12,
                'placeholder': 'Votre Message...'
            }
        )
    )
