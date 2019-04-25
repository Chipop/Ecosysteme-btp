from django.db import models
from django.contrib.auth.models import User, AnonymousUser
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
from django.urls import reverse
from django.utils.deconstruct import deconstructible

import os
import uuid

import ao


# For rename the file before save
@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        # eg: filename = 'my uploaded file.jpg'
        ext = filename.split('.')[-1]  # eg: 'jpg'
        uid = uuid.uuid4().hex[:10]  # eg: '567ae32f97'

        # eg: 'my-uploaded-file'
        new_name = '-'.join(filename.replace('.%s' % ext, '').split())

        # eg: 'my-uploaded-file_64c942aa64.jpg'
        renamed_filename = '%(new_name)s_%(uid)s.%(ext)s' % {'new_name': new_name, 'uid': uid, 'ext': ext}

        # eg: 'images/2017/01/29/my-uploaded-file_64c942aa64.jpg'
        return os.path.join(self.path, renamed_filename)

class Image(models.Model):
    image = models.ImageField(default="")

    def __str__(self):
        return str(self.image)


class TypeEntreprise(models.Model):
    types = (('publique', 'publique'), ('prive', 'prive'))
    type = models.CharField(max_length=255, choices=types)


class Entreprise(models.Model):
    types = (('Petite entreprise', 'Petite entreprise'), ('Grande entreprise', 'Grande entreprise'),
             ('Très petite entreprise', 'Très petite entreprise'), ('Moyenne entreprise', 'Moyenne entreprise'))
    secteurs = (('Publique', 'Publique'), ('Prive', 'Privé'))
    nom = models.CharField(max_length=300, null=True, blank=False, unique=True)
    activite = models.CharField(max_length=255, null=True, blank=False)
    secteurActivite = models.CharField(choices=secteurs, null=True, blank=False, max_length=255)
    capitale = models.DecimalField(null=True, blank=False, decimal_places=2, max_digits=10)
    pays = models.CharField(max_length=255, blank=True, null=False)
    ville = models.CharField(max_length=255, null=True, blank=False)
    codePostal = models.IntegerField(null=True)
    telephone = models.IntegerField(null=True)
    typeEntreprise = models.CharField(max_length=255, choices=types)
    raison_social = models.CharField(max_length=255, blank=False, null=True)
    registre_commerce = models.CharField(max_length=255, blank=False, null=True)
    fax = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    email_entreprise = models.EmailField(null=True)
    adresse_Entreprise = models.CharField(max_length=255, blank=False, null=True)
    logo = models.FileField(upload_to="", null=True, blank=False)

    @staticmethod
    def noms_entreprises():
        noms_entreprises = ""
        for entreprise in Entreprise.objects.all():
            noms_entreprises += entreprise.nom + ","
        return noms_entreprises[:-1]

    def __str__(self):
        return self.nom


class Profil(models.Model):
    CIVILITE_CHOICES = [('Mr', 'Mr'),
                        ('Mme', 'Mme'),
                        ('Mlle', 'Mlle'),
                        ]
    ACTIVITE_CHOICES = [
        ('Administration publique', 'Administration publique'),
        ('Architecture', 'Architecture'),
        ('Association, organisme professionnel', 'Association, organisme professionnel'),
        ('Bâtiment', 'Bâtiment'),
        ('Aménagement urbain', 'Aménagement urbain'),
        ('Collectivités locales - territoriales', 'Collectivités locales - territoriales'),
        ('Commerce - Grande distribution', 'Commerce - Grande distribution'),
        ('Communication - Edition', 'Communication - Edition'),
        ('Conseil - Etudes - Ingénierie', 'Conseil - Etudes - Ingénierie'),
        ('Contrôle technique', 'Contrôle technique'),
        ('Education - Formation', 'Education - Formation'),
        ('Energie', 'Energie'),
        ('Environnement - Développement durable', 'Environnement - Développement durable'),
        ('Finance - Banque - Assurance', 'Finance - Banque - Assurance'),
        ('Hôtellerie - Restauration - Tourisme', 'Hôtellerie - Restauration - Tourisme'),
        ('Immobilier', 'Immobilier'),
        ('Informatique - Télécommunications', 'Informatique - Télécommunications'),
        ('Juridique', 'Juridique'),
        ('Matériaux', 'Matériaux'),
        ('Matériel, outillage et procédés', 'Matériel, outillage et procédés'),
        ('Mobilier et décoration', 'Mobilier et décoration'),
        ('Recherche (Organisme - Laboratoire)', 'Recherche (Organisme - Laboratoire)'),
        ('Transport - Logistique', 'Transport - Logistique'),
        ('Travaux spéciaux', 'Travaux spéciaux'),
        ('Autres', 'Autres'),
    ]

    SECTEUR_CHOICES = [
        ('Privé', 'Au secteur privé'),
        ('Public', 'Au secteur public')
    ]

    TAILLE_ENTREPRISE_CHOICES = [
        ('1 à 10 salariés', '1 à 10 salariés'),
        ('11 à 20 salariés', '11 à 20 salariés'),
        ('21 à 50 salariés', '21 à 50 salariés'),
        ('51 à 249 salariés', '51 à 249 salariés'),
        ('250 à 500 salariés', '250 à 500 salariés'),
        ('501 à 1 000 salariés', '501 à 1 000 salariés'),
        ('Plus de 1 000 salariés', 'Plus de 1 000 salariés'),
    ]

    FONCTION_CHOICES = [
        ('Agent de service public', 'Agent de service public'),
        ('Architecte', 'Architecte'),
        ('Artisan', 'Artisan'),
        ('Chef de projet', 'Chef de projet'),
        ('Commerçant', 'Commerçant'),
        ('Consultant', 'Consultant'),
        ('Directeur - Chef de service', 'Directeur - Chef de service'),
        ('Direction générale(PDG, DG, Gérant)', 'Direction générale(PDG, DG, Gérant)'),
        ('Elu local, Conseiller municipaux', 'Elu local, Conseiller municipaux'),
        ('Elu territorial, Conseiller Général / Conseil Régional',
         'Elu territorial, Conseiller Général / Conseil Régional'),
        ('Enseignant chercheur', 'Enseignant chercheur'),
        ('Etudiant', 'Etudiant'),
        ('Haut fonctionnaire(Etat / Ministères)', 'Haut fonctionnaire(Etat / Ministères)'),
        ('Ingénieur', 'Ingénieur'),
        ('Président, Vice - Président', 'Président, Vice - Président'),
        ('Responsable - Chargé - Attaché', 'Responsable - Chargé - Attaché'),
        ('Technicien', 'Technicien'),
        ('Urbaniste - Paysagiste', 'Urbaniste - Paysagiste'),
        ('Autre', 'Autre'),
    ]

    DEPARTEMENT_CHOICES = [
        ('Achat', 'Achat'),
        ('Commercial', 'Commercial'),
        ('Communication, Evénementiel', 'Communication, Evénementiel'),
        ('Construction, Immobilier, Infrastrcutures', 'Construction, Immobilier, Infrastrcutures'),
        ('Développement durable', 'Développement durable'),
        ('Développement économique', 'Développement économique'),
        ('Eaux', 'Eaux'),
        ('Environnement', 'Environnement'),
        ('Espaces verts, Biodiversité', 'Espaces verts, Biodiversité'),
        ('Etude', 'Etude'),
        ('Exploitation', 'Exploitation'),
        ('Export - Import', 'Export - Import'),
        ('Finance', 'Finance'),
        ('Hygiène - Sécurité', 'Hygiène - Sécurité'),
        ('Informatique', 'Informatique'),
        ('Juridique', 'Juridique'),
        ('Logistique - transport', 'Logistique - transport'),
        ('Maintenance', 'Maintenance'),
        ('Qualité, méthodes', 'Qualité, méthodes'),
        ('Recherche & Développement', 'Recherche & Développement'),
        ('Ressources humaines', 'Ressources humaines'),
        ('Restauration', 'Restauration'),
        ('Santé, Affaires sociales', 'Santé, Affaires sociales'),
        ('Service Technique', 'Service Technique'),
        ('Services généraux', 'Services généraux'),
        ('Technique - Production', 'Technique - Production'),
        ('Transports urbains', 'Transports urbains'),
        ('Usine - Site', 'Usine - Site'),
        ('Autre', 'Autre'),
    ]

    date_naissance = models.DateField(null=True, blank=True)
    website = models.CharField(max_length=300, default="", null=True, blank=True)
    entreprise = models.ForeignKey(Entreprise, blank=True, null=True, on_delete=models.CASCADE, default=None)
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.CASCADE)
    photo_profil = models.ForeignKey(Image, blank=True, null=True, on_delete=models.CASCADE,
                                     related_name="profil_photo", default=None)
    photo_couverture = models.ForeignKey(Image, blank=True, null=True, on_delete=models.CASCADE,
                                         related_name="photo_cover", default=None)
    facebook = models.CharField(max_length=300, blank=True, null=True, default="")
    youtube = models.CharField(max_length=300, blank=True, null=True, default="")
    instagram = models.CharField(max_length=300, blank=True, null=True, default="")
    linkedin = models.CharField(max_length=300, blank=True, null=True, default="")
    twitter = models.CharField(max_length=300, blank=True, null=True, default="")
    tel = models.CharField(max_length=300, blank=True, null=True, default="")
    tel_portable = models.CharField(max_length=300, blank=True, null=True, default="")
    telecopie = models.CharField(max_length=300, blank=True, null=True, default="")
    ville = models.CharField(max_length=300, default="")
    pays = models.CharField(max_length=300, default="")
    token_email = models.CharField(max_length=300, blank=True, null=True, default="")
    token_email_expiration = models.DateTimeField(blank=True, null=True)
    civilite = models.CharField(max_length=255, choices=CIVILITE_CHOICES)
    code_postal = models.CharField(max_length=255)
    adresse_profile = models.CharField(max_length=255)
    adresse_profile2 = models.CharField(max_length=255, blank=True, null=True)
    is_first_appoffre = models.BooleanField(default=True)
    formation_profil = models.ForeignKey('SocialMedia.Formation', on_delete=models.CASCADE, blank=True, null=True,
                                         related_name="formation_profil", default=None)
    experience_profil = models.ForeignKey('SocialMedia.Experience', on_delete=models.CASCADE, blank=True, null=True,
                                          related_name="experience_profil", default=None)
    resume = models.CharField(max_length=300, blank=True, null=True, default="")
    is_professional = models.BooleanField(default=False)
    is_journaliste = models.BooleanField(default=False)
    is_etudiant = models.BooleanField(default=False)
    is_particulier = models.BooleanField(default=False)
    is_active_professional = models.BooleanField(default=False, verbose_name="Compte Activé par l'administration")
    is_supplier = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False)

    points = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    connecte = models.IntegerField(default=0, blank=True, null=True)

    fonction = models.CharField(max_length=300, default="", choices=FONCTION_CHOICES, null=True, blank=True)
    secteur = models.CharField(max_length=300, default="", choices=SECTEUR_CHOICES, null=True, blank=True)
    service = models.CharField(max_length=300, default="", null=True, blank=True)
    activite = models.CharField(max_length=300, default="", choices=ACTIVITE_CHOICES, null=True, blank=True)
    taille_entreprise = models.CharField(max_length=300, default="", choices=TAILLE_ENTREPRISE_CHOICES, null=True,
                                         blank=True)
    departement = models.CharField(max_length=300, default="", choices=DEPARTEMENT_CHOICES, null=True, blank=True)
    nom_entreprise = models.CharField(max_length=300, default="", null=True, blank=True)
    socialmedia_profil_views_number  = models.IntegerField(default=0)

    qa_view = models.IntegerField(default=0)

    # elearning attributes
    is_teacher = models.BooleanField(default=False)
    request_teacher = models.BooleanField(default=False)
    teacher_title = models.CharField(max_length=300, default="", null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    view_teacher = models.IntegerField(default=1, null=False, blank=False)
    cv = models.FileField(null=False, blank=False, upload_to=PathAndRename('CV'),default="")  # to change to null False

    blacklisted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name.title() + " " + self.user.last_name.title() + " ( " + self.user.email + " )"

    def se_connecte(self):
        if not isinstance(self.connecte, int):
            self.connecte = 1
        else:
            self.connecte = self.connecte + 1

    def se_deconnecte(self):
        self.connecte = self.connecte - 1

    def count_lots(self):
        aos = ao.models.AO.objects.filter(user=self)
        return ao.models.Project.objects.filter(ao__in=aos).count()

    def get_lots(self):
        aos = ao.models.AO.objects.filter(user=self)
        return ao.models.Project.objects.filter(ao__in=aos)

    def type(self):
        if self.is_etudiant:
            return "Etudiant"
        elif self.is_particulier:
            return "Particulier"
        elif self.is_journaliste:
            return "Journaliste"
        elif self.is_professional:
            return "Professionnel"

    class Meta:
        verbose_name_plural = "Profils"
        verbose_name = "Profil"

    def tracking_get_admin_url(self):
        return reverse('dashboard:socialmedia_infos_profile', kwargs={'id_user': self.id})

    def tracking_get_absolute_url(self):
        return reverse('SocialMedia:getProfil', kwargs={'pk': self.id})

    def tracking_get_description(self):
        return self.user.first_name.title() +" "+ self.user.last_name.title()


class Contact(models.Model):
    full_name = models.CharField(max_length=300)
    sujet = models.CharField(max_length=300, default="")
    email = models.EmailField()
    message = models.TextField(default="")
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=300, default="-")
    lu = models.BooleanField(default=False)
    important = models.BooleanField(default=False)
    repondu = models.BooleanField(default=False)
    reponse = RichTextUploadingField(default="")

    def __str__(self):
        return self.full_name


class NewsLetterMails(models.Model):
    email = models.EmailField()
    type = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.email

