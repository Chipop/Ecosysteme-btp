from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password


class FormUserInscription(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput())
    confirmer_votre_mot_de_passe = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password')

    def clean(self):
        print("cleana User")
        cleaned_data = super(FormUserInscription, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirmer_votre_mot_de_passe")

        email = cleaned_data.get('email')
        username = cleaned_data.get('username')

        if email and User.objects.filter(email=email).exclude(username=username).exists():
            self.add_error('email', "Cet E-mail est déjà enregistré.")

        if password != confirm_password:
            self.add_error("password", "Les deux mot de passes ne sont pas identiques.")

        try:
            validate_password(password=password, )
        except forms.ValidationError as e:
            error_message = list(e.messages)
            for error in error_message:
                self.add_error("password", error + "<br>")


CIVILITE_CHOICES = [('Mr', 'Mr'),
                 ('Mme', 'Mme'),
                 ('Mlle', 'Mlle'),
                 ]

class FormProfilInscription(forms.ModelForm):
    PROFILE_CHOICES = [
        ('Vous êtes un professionnel','Vous êtes un professionnel'),
        ('Vous êtes un particulier','Vous êtes un particulier'),
        ('Vous êtes un étudiant', 'Vous êtes un étudiant'),
        ('Vous êtes un journaliste/éditeur', 'Vous êtes un journaliste/éditeur'),
    ]
    votre_profile = forms.ChoiceField(choices=PROFILE_CHOICES)
    civilite = forms.ChoiceField(choices= CIVILITE_CHOICES,widget=forms.RadioSelect())
    autres = forms.CharField(max_length=300,required=False)

    class Meta:
        model = Profil
        fields = ['civilite', 'nom_entreprise', 'adresse_profile', 'adresse_profile2','code_postal', 'ville', 'pays', 'tel',
                  'tel_portable', 'telecopie','website','activite','taille_entreprise','fonction','departement' ]

    def clean(self):
        cleaned_data = super(FormProfilInscription, self).clean()
        activite = cleaned_data.get("activite")
        taille_entreprise = cleaned_data.get("taille_entreprise")
        fonction = cleaned_data.get("fonction")
        departement = cleaned_data.get("departement")
        votre_profil = cleaned_data.get("votre_profile")
        autres = cleaned_data.get("autres")

        print("cleana m3a rassou ...")
        if votre_profil == 'Vous êtes un professionnel' or votre_profil == 'Vous êtes un journaliste/éditeur':
            if activite is None :
                self.add_error("activite", "Ce champ est obligatoire.")
            if taille_entreprise  is None:
                self.add_error("taille_entreprise", "Ce champ est obligatoire.")
            if fonction  is None:
                self.add_error("fonction", "Ce champ est obligatoire.")
            if departement  is None:
                self.add_error("departement", "Ce champ est obligatoire.")
            if activite == "Autres" and autres  is None:
                self.add_error("autres", "En choisissant 'Autres', Ce champ est obligatoire.")


class loginform(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['email', 'password']


class userform(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'first_name', 'last_name']


class userProfile(forms.ModelForm):
    class Meta:
        model = Profil
        exclude = ['last_logout', 'user']


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = '__all__'


class formConfirmEmail(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['full_name','email','message']
