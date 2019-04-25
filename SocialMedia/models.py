

from django.db import models
from django.contrib.auth.models import User
import os.path
from django.urls import reverse
from itertools import chain
from django.db.models import Max
from django.utils.timezone import now
import datetime


class Groupe(models.Model):
    statuts = (('publique', 'publique'), ('prive', 'privé'))

    nom = models.CharField(max_length=255)
    date_creation = models.DateField()
    statut_groupe = models.CharField(choices=statuts, max_length=255, null=False, blank=False)
    have_image = models.BooleanField(default=False)
    description = models.TextField(default="")
    photo_profil = models.ForeignKey('main_app.Image', on_delete=models.CASCADE, related_name="groupe_photo")
    photo_couverture = models.ForeignKey('main_app.Image', on_delete=models.CASCADE, related_name="profil_cover")
    admins = models.ManyToManyField('main_app.Profil', related_name="admin")
    moderators = models.ManyToManyField('main_app.Profil', related_name="moderateur")
    creator = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="createur")
    adherents = models.ManyToManyField('main_app.Profil', related_name="adherent")
    views_number = models.IntegerField(default=0)

    def __str__(self):
        return "Groupe: " + self.nom + "\b\bCree Par: " + self.creator.user.username

    def get_absolute_url(self):
        return reverse('SocialMedia:groupe', args=[str(self.id)])

    class Meta:
        verbose_name_plural = 'Groupes'
        verbose_name = "Groupe"

    def tracking_get_admin_url(self):
        return reverse('dashboard:socialmedia_infos_group', kwargs={'id_group': self.id})

    def tracking_get_absolute_url(self):
        return reverse('SocialMedia:groupe', kwargs={'pk': self.id})

    def tracking_get_description(self):
        return self.nom


class DemandeGroupe(models.Model):
    emetteur = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)
    groupe_recepteur = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    reponse = models.BooleanField()

    def __str__(self):
        return self.emetteur.user.username + " à demandé de rejoidre le groupe " + self.groupe_recepteur.nom


def generate_path(instance, filename):
    extension = os.path.splitext(filename)[1][1:]
    if extension in VALID_IMAGE_EXTENSIONS:
        path = 'SocialMedia/Image/'
    else:
        path = 'SocialMedia/Fichier/'

    return os.path.join(path, instance.fichier.name)


class ReseauSocialFile(models.Model):
    fichier = models.FileField(upload_to=generate_path)
    date_telechargement = models.DateTimeField()
    profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="FileOwner")

    def __str__(self):
        return self.fichier.name


class DemandeAmi(models.Model):
    demandes = ((0, 'En Cours'), (1, 'Acceptée'), (2, 'Refusée'), (3, 'Bloquée'))
    emetteur = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="sender")
    recepteur = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="receiver")
    statut = models.IntegerField(null=False, blank=False, choices=demandes)

    @staticmethod
    def sont_ami(user1, user2):
        demande_acceptee = get_object_or_none(DemandeAmi, emetteur=user1.profil, recepteur=user2.profil, statut=1)
        demande_acceptee2 = get_object_or_none(DemandeAmi, emetteur=user2.profil, recepteur=user1.profil, statut=1)

        if demande_acceptee is not None or demande_acceptee2 is not None:
            return True
        return False

    @staticmethod
    def nb_amis(profil):

        try:
            demande_acceptee = DemandeAmi.objects.filter(recepteur=profil, statut=1).count()
        except:
            demande_acceptee = 0

        try:
            demande_acceptee2 = DemandeAmi.objects.filter(emetteur=profil, statut=1).count()
        except Exception as e:
            demande_acceptee2 = 0

        return demande_acceptee + demande_acceptee2

    def __str__(self):
        return self.demandes[self.statut][1]


class Suivie(models.Model):
    follower = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="suiveur")
    followed_profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="suivi", null=True)

    class Meta:
        unique_together = ('follower', 'followed_profil',)

    def __str__(self):
        return self.follower.user.username + " suit " + self.followed_profil.user.username


class Conversation(models.Model):
    start_date = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(User)
    id_chat = models.CharField(max_length=1000)

    def __str__(self):
        show = ""
        for user in self.participants.all():
            show += " || Participant Username: " + user.username
        return show


class MessageConversation(models.Model):
    message = models.CharField(max_length=6000)
    date = models.DateTimeField(auto_now_add=True)
    is_image = models.BooleanField(default=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    image = models.ForeignKey("main_app.Image", on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return "Response Of: " + self.user.username


VALID_IMAGE_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png",
    "gif",
]


class Poste(models.Model):
    nom_poste = models.CharField(max_length=300)

    @staticmethod
    def noms_postes():
        noms_postes = ""
        for poste in Poste.objects.all():
            noms_postes += poste.nom_poste + ","
        return noms_postes[:-1]

    def __str__(self):
        return self.nom_poste


class PageEntreprise(models.Model):
    entreprise = models.OneToOneField("main_app.Entreprise", blank=False, null=True, on_delete=models.CASCADE)
    presentation_entreprise = models.CharField(max_length=3000, blank=False, null=True)
    siege_social = models.CharField(max_length=255, blank=False, null=True)
    annee_creation = models.IntegerField(null=True, blank=False)
    specialisation = models.CharField(max_length=255, blank=False, null=True)
    abonnees = models.ManyToManyField('main_app.Profil', related_name="abonnees", blank=True)
    administrateurs = models.ManyToManyField('main_app.Profil', related_name="administrateurs", blank=True)
    moderateurs = models.ManyToManyField('main_app.Profil', related_name="moderateurs", blank=True)
    img_couverture = models.ImageField(upload_to="", null=True, blank=True)
    views_number = models.IntegerField(default=0)

    def is_administrateur(self, user):
        if user.profil not in self.administrateurs.all():
            return False
        return True

    def is_moderateur(self, user):
        if user.profil not in self.moderateurs.all():
            return False
        return True

    def employes(self):
        return Experience.objects.filter(entreprise=self.entreprise, actuel=True).values('profil')

    class Meta:
        verbose_name_plural = 'Pages Entreprise'
        verbose_name = "Page Entreprise"

    def tracking_get_admin_url(self):
        return reverse('dashboard:socialmedia_infos_page_entreprise', kwargs={'id_page_entreprise': self.id})

    def tracking_get_absolute_url(self):
        return reverse('SocialMedia:page_entreprise', kwargs={'id_page_entreprise': self.id})

    def tracking_get_description(self):
        return self.entreprise.nom

    def __str__(self):
        return self.entreprise.nom

    def get_absolute_url(self):
        return reverse('SocialMedia:page_entreprise', args=[str(self.entreprise_id)])


class OffreEmploi(models.Model):
    TYPES_EMPLOI = (('plein', 'Plein temps'), ('partiel', 'Temps partiel'))
    TYPES_CONTRAT = (('cdi', 'CDI'), ('cdd', 'CDD'))

    tel = models.IntegerField()
    email = models.EmailField()
    pays = models.CharField(max_length=300)
    ville = models.CharField(max_length=300)
    diplome_requis = models.CharField(max_length=300)
    type_contrat = models.CharField(max_length=300, choices=TYPES_CONTRAT)
    description_poste = models.TextField()
    profil_recherche = models.TextField()
    date_publication = models.DateField(auto_now_add=True)
    en_cours = models.BooleanField(default=True)
    date_fin = models.DateField(null=True, default=None, blank=True)
    type_emploi = models.CharField(max_length=300, choices=TYPES_EMPLOI)
    poste = models.ForeignKey(Poste, on_delete=models.CASCADE,
                              related_name="poste_recherche", null=True)
    nom_poste = models.CharField(max_length=300)
    page_entreprise = models.ForeignKey(PageEntreprise, on_delete=models.CASCADE)
    profil_publicateur = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE,
                                           related_name="profil_publicateur")
    profil_postulants = models.ManyToManyField('main_app.Profil', related_name="profil_postulants", blank=True)
    fichier_joint = models.FileField(null=True, blank=True)
    views_number = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)

    def __str__(self):
        return self.page_entreprise.entreprise.nom + " propose un poste d'un " + self.nom_poste

    class Meta:
        verbose_name_plural = "Offres d'emploi"
        verbose_name = "Offre d'emploi"

    def tracking_get_admin_url(self):
        return reverse('dashboard:socialmedia_infos_offre_emploi', kwargs={'id_offre_emploi': self.id})

    def tracking_get_absolute_url(self):
        return reverse('SocialMedia:page_offre_emploi', kwargs={'id_offre_emploi': self.id})

    def tracking_get_description(self):
        return self.nom_poste + " par " + self.page_entreprise.entreprise.nom

    def add_share(self):
        self.shares += 1
        self.save()


class Experience(models.Model):
    entreprise = models.ForeignKey('main_app.Entreprise', on_delete=models.CASCADE, null=True, blank=True)
    nom_entreprise = models.CharField(max_length=300)
    poste = models.ForeignKey(Poste, on_delete=models.CASCADE, null=True, blank=True)
    nom_poste = models.CharField(max_length=300)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    actuel = models.BooleanField()
    description = models.TextField(null=True, blank=True)
    lieu = models.CharField(max_length=300, null=True, blank=True)
    profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)

    def regler_date(self):
        self.date_debut = self.date_debut.replace(day=1)
        self.date_fin = self.date_fin.replace(day=1)

    @staticmethod
    def get_user_experiences(user):
        exp = Experience.objects.filter(profil=user.profil).exclude(date_fin=None).order_by(
            '-date_fin')  # Experiences passées
        exp2 = Experience.objects.filter(profil=user.profil, date_fin=None)  # Experience actuelle
        return list(chain(exp2, exp))

    def __str__(self):
        return self.nom_poste + " à " + self.nom_entreprise


class Ecole(models.Model):
    nom = models.CharField(max_length=300)
    logo = models.ImageField(upload_to="SocialMedia/Image/")

    @staticmethod
    def noms_ecoles():
        noms_ecoles = ""
        for ecole in Ecole.objects.all():
            noms_ecoles += ecole.nom + ","

        return noms_ecoles[:-1]

    def __str__(self):
        return self.nom


class Formation(models.Model):
    titre_formation = models.CharField(max_length=300)
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE, null=True, blank=True)
    nom_ecole = models.CharField(max_length=300)
    domaine = models.CharField(max_length=300, null=True, blank=True)
    activite_et_associations = models.TextField(null=True, blank=True)
    annee_debut = models.DateField()
    annee_fin = models.DateField()
    description = models.TextField(null=True, blank=True)
    profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)

    @staticmethod
    def get_last_formation(user):
        max_annee_fin = Formation.objects.filter(profil=user.profil).aggregate(Max('annee_fin'))['annee_fin__max']
        return Formation.objects.filter(profil=user.profil, annee_fin=max_annee_fin).first()

    def regler_date(self):
        self.date_debut = self.annee_debut.replace(day=1)
        self.date_fin = self.annee_fin.replace(day=1)
        self.date_fin = self.annee_debut.replace(month=1)
        self.date_fin = self.annee_fin.replace(month=1)

    @staticmethod
    def get_user_formations(user):
        return Formation.objects.filter(profil=user.profil).order_by('-annee_fin')  # Formations passées

    def __str__(self):
        return self.titre_formation + " à " + self.nom_ecole


class Organisme(models.Model):
    nom = models.CharField(max_length=300)
    logo = models.ImageField(upload_to="SocialMedia/Image/")

    @staticmethod
    def noms_organismes():
        noms_organismes = ""
        for organisme in Organisme.objects.all():
            noms_organismes += organisme.nom + ","

        return noms_organismes[:-1]

    def __str__(self):
        return self.nom


class ActionBenevole(models.Model):
    organisme = models.ForeignKey(Organisme, on_delete=models.CASCADE, null=True, blank=True)
    nom_organisme = models.CharField(max_length=300)
    poste = models.ForeignKey(Poste, on_delete=models.CASCADE, null=True, blank=True)
    nom_poste = models.CharField(max_length=300)
    cause = models.TextField(null=True, blank=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    description = models.TextField(null=True, blank=True)
    profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)

    @staticmethod
    def get_user_benevolats(user):
        return ActionBenevole.objects.filter(profil=user.profil).order_by('-date_fin')  # Benevolats passés

    def regler_date(self):
        self.date_debut = self.date_debut.replace(day=1)
        self.date_fin = self.date_fin.replace(day=1)

    def __str__(self):
        return self.profil.user.first_name + " " + self.profil.user.last_name + " fait  " + self.nom_poste + " à " + self.nom_organisme


class Langue(models.Model):
    nom = models.CharField(max_length=300)

    def __str__(self):
        return self.nom


class NiveauLangue(models.Model):
    niveau = models.CharField(max_length=300)

    def __str__(self):
        return self.niveau


class LangueProfil(models.Model):
    profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, null=True, blank=True)
    langue = models.ForeignKey(Langue, on_delete=models.CASCADE)
    niveau = models.ForeignKey(NiveauLangue, on_delete=models.CASCADE)


def get_object_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


"""""""""""
class Statut(models.Model):
    is_shared = models.BooleanField(default=False)
    original_statut_id = models.IntegerField(null=True, blank=True)
    date_statut = models.DateTimeField()
    contenu_statut = models.CharField(max_length=6000)
    is_group_statut = models.BooleanField(default=False)
    is_profil_statut = models.BooleanField(default=False)
    publisher = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="pub")
    mur_profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, null=True, blank=True,
                                   related_name="statut_mur_profil")
    mur_groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, null=True, blank=True)
    images = models.ManyToManyField(ReseauSocialFile, related_name="images", blank=True)
    videos = models.ManyToManyField(ReseauSocialFile, related_name="videos", blank=True)
    files = models.ManyToManyField(ReseauSocialFile, related_name="files", blank=True)
    likes = models.ManyToManyField('main_app.Profil', blank=True, related_name="profil_likes_statut")
    shares_number = models.IntegerField(default=0)
    views_number = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Statuts'
        verbose_name = "Statut"

    def tracking_get_admin_url(self):
        return reverse('dashboard:socialmedia_infos_publication', kwargs={'id_publication': self.id})

    def tracking_get_absolute_url(self):
        return reverse('SocialMedia:Statut', kwargs={'pk': self.id})

    def tracking_get_description(self):
        return self.contenu_statut[:20]

    def __str__(self):
        return self.publisher.user.username + " a publié un statut " + self.contenu_statut[:30]

    def get_absolute_url(self):
        return reverse('SocialMedia:Statut', args=[str(self.id)])

    def shares(self):
        return Statut.objects.filter(is_shared=True, original_statut_id=self.id).count()

"""""""""""


class AbstractStatut(models.Model):
    date_statut = models.DateTimeField(auto_now_add=True)
    contenu_statut = models.CharField(max_length=6000,default="")
    publisher = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="publisher_statut",default=1)
    mur_profil = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, null=True, blank=True,
                                   related_name="statut_mur_profil",default=1)

    likes = models.ManyToManyField('main_app.Profil', blank=True, related_name="profil_likes_statut")
    views_number = models.IntegerField(default=0)

    def get_max_comment_id(self):
        return self.commentaire_set.filter(parent=None).aggregate(max=Max('id'))['max']

    def get_commentaires(self):
        return self.commentaire_set.filter(parent=None)

    def get_absolute_url(self):
        return reverse('SocialMedia:Statut', kwargs={'pk': self.id} )



    def get_signals(self):
        return self.statut_signales.filter(active=True)


class Statut(AbstractStatut):
    is_group_statut = models.BooleanField(default=False)
    is_profil_statut = models.BooleanField(default=False)
    is_entreprise_statut = models.BooleanField(default=False)

    is_link_statut = models.BooleanField(default=False)
    link_icon = models.CharField(max_length=1000, default="", null=True, blank=True,)
    link_title = models.CharField(max_length=1000, default="", null=True, blank=True,)
    link_description = models.CharField(max_length=1000, default="", null=True, blank=True,)
    link_url = models.CharField(max_length=1000, default="", null=True, blank=True,)

    mur_groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, null=True, blank=True,
                                   related_name="statut_mur_groupe")
    mur_entreprise = models.ForeignKey(PageEntreprise, on_delete=models.CASCADE, null=True, blank=True,
                                       related_name="statut_mur_entreprise")

    images = models.ManyToManyField(ReseauSocialFile, related_name="images", blank=True)
    videos = models.ManyToManyField(ReseauSocialFile, related_name="videos", blank=True)
    files = models.ManyToManyField(ReseauSocialFile, related_name="files", blank=True)


    class Meta:
        verbose_name_plural = 'Statuts'
        verbose_name = "Statut"

    # Original = statut nom  partagé
    # shared = statut partgé
    def type(self):
        return "original"

    def tracking_get_admin_url(self):
        return reverse('dashboard:socialmedia_infos_publication', kwargs={'id_publication': self.id})

    def tracking_get_absolute_url(self):
        return reverse('SocialMedia:Statut', kwargs={'pk': self.id})

    def tracking_get_description(self):
        return self.contenu_statut[:20]

    def __str__(self):
        return self.publisher.user.username + " a publié un statut " + self.contenu_statut[:30]

    def shares(self):
        return SharedStatut.objects.filter(shared_statut=self).count()

    def type_statut(self):
        if self.is_group_statut:
            return "Groupe"
        elif self.is_entreprise_statut:
            return "Page d'entreprise"
        else:
            return "Profil"


class SharedStatut(AbstractStatut):
    shared_statut = models.ForeignKey(Statut,on_delete=models.CASCADE,related_name="shared_statut")
    date_share = models.DateTimeField(auto_now_add=True)

    # Original = statut nom  partagé
    # shared = statut partgé
    def type(self):
        return "shared"

    class Meta:
        verbose_name_plural = 'Statut partagé'
        verbose_name = "Statut partagé"

    def tracking_get_admin_url(self):
        return reverse('dashboard:socialmedia_infos_publication', kwargs={'id_publication': self.id})

    def tracking_get_absolute_url(self):
        return reverse('SocialMedia:Statut', kwargs={'pk': self.id})

    def tracking_get_description(self):
        return self.contenu_statut[:20]


class Commentaire(models.Model):
    TYPE_STATUT_CHOICES = (('original','original'),('shared','shared'))
    content = models.TextField(null=False, blank=False)
    date_commentaire = models.DateTimeField(auto_now_add=True)
    statut = models.ForeignKey(AbstractStatut, on_delete=models.CASCADE)
    type_statut = models.CharField(max_length=15, default="original",choices=TYPE_STATUT_CHOICES)
    user = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE, related_name="commented_user")
    image = models.ForeignKey(ReseauSocialFile, blank=True,null=True,on_delete=models.CASCADE)
    likes = models.ManyToManyField('main_app.Profil', blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.content

    def replies(self):
        return self.commentaire_set.all()

    def count_replies(self):
        return self.commentaire_set.all().count()

    class Meta:
        ordering = ['-date_commentaire']

    def get_related_statut(self):
        print(self.type_statut)
        if self.type_statut == "original":
            return Statut.objects.get(id=self.statut.id)
        else:
            return SharedStatut.objects.get(id=self.statut.id)



class StatutSignales(models.Model):
    statut_signale = models.ForeignKey(AbstractStatut, on_delete=models.CASCADE, related_name="statut_signales")
    active = models.BooleanField(default=True)
    signal_sender = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)
    cause = models.CharField(max_length=1000, default="")
    type = models.CharField(max_length=15, default="original")
    date_signale = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_signale']


class CommentaireSignales(models.Model):
    commentaire = models.ForeignKey(Commentaire, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    signal_sender = models.ForeignKey('main_app.Profil', on_delete=models.CASCADE)
    cause = models.CharField(max_length=1000, default="")
    date_signale = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_signale']


class Notification(models.Model):
    types = ((0, 'statut'),
             (1, 'groupe'),
             (2, 'profil'),
             (3, 'offreEmploi'),
             (4, 'entreprise'),
             (5, 'demande'))
    statut = models.ForeignKey(Statut, on_delete=models.CASCADE, null=True, blank=True)
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE, null=True, blank=True)
    profil = models.ForeignKey('main_app.Profil', related_name='profil', on_delete=models.CASCADE, null=True,
                               blank=True)
    offreEmploi = models.ForeignKey(OffreEmploi, on_delete=models.CASCADE, null=True, blank=True)
    entreprise = models.ForeignKey(PageEntreprise, on_delete=models.CASCADE, null=True, blank=True)
    type = models.IntegerField(choices=types, null=True, blank=True)
    message = models.CharField(max_length=1000)
    is_read = models.BooleanField(default=False)
    read_date = models.DateTimeField(null=True, blank=True)
    date_notification = models.DateTimeField(default=now)
    profil_to_notify = models.ForeignKey('main_app.Profil', related_name='profil_to_notify', null=True, blank=True,
                                         on_delete=models.CASCADE)

    def __str__(self):
        return self.message
