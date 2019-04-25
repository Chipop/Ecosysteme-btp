from django.contrib import admin
from .models import *
from django.utils.safestring import mark_safe
from django.urls import resolvers


# Register your models here.


class DemandeAmiAdmin(admin.ModelAdmin):
    list_display = ['emetteur', 'recepteur', 'statut']
    list_filter = ['emetteur', 'recepteur', 'statut']
    empty_value_display = '-vide-'


class DemandeGroupeAdmin(admin.ModelAdmin):
    list_display = ['emetteur', 'nom_groupe', 'reponse']
    list_filter = ['emetteur', 'groupe_recepteur', 'reponse']
    empty_value_display = '-vide-'

    def nom_groupe(self, obj):
        return obj.groupe_recepteur.nom


class ActionsBenevoleAdmin(admin.ModelAdmin):
    list_display = ['organisme', 'nom_organisme', 'poste', 'nom_poste', 'date_fin', 'date_debut', 'profil']
    list_filter = ['organisme', 'nom_organisme', 'poste', 'nom_poste', 'date_fin', 'date_debut', 'profil']
    empty_value_display = '-vide-'


class CommentaireSignalesAdmin(admin.ModelAdmin):
    list_display = ['commentaire_signale', "proprietaire_du_commentaire", 'Utilisateur_qui_a_signale']
    empty_value_display = '-vide-'

    def commentaire_signale(self, obj):
        return obj.commentaire.comment

    def Utilisateur_qui_a_signale(self, instance):
        return instance.signal_sender.user.first_name + " " + instance.signal_sender.user.last_name

    def proprietaire_du_commentaire(self, instance):
        return instance.commentaire.user.user.first_name + " " + instance.commentaire.user.user.last_name




class EcoleAdmin(admin.ModelAdmin):
    list_display = ['nom', 'display_image']
    empty_value_display = '-vide-'

    def display_image(self, obj):
        if obj.logo:
            return mark_safe('<img src="{url}" width="100px" height="50px" />'.format(url=obj.logo.url))


class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['entreprise', 'nom_entreprise', 'poste', 'nom_poste', 'nom_poste', 'date_debut', 'date_fin',
                    'actuel', 'description', 'lieu', 'profil']

    empty_value_display = '-vide-'


class FormationAdmin(admin.ModelAdmin):
    list_display = ['titre_formation', 'ecole', 'nom_ecole', 'domaine', 'activite_et_associations', 'annee_debut',
                    'annee_fin', 'description', 'profil']

    search_fields = ['titre_formation', 'nom_ecole', 'annee_debut', 'annee_fin', 'domaine']
    empty_value_display = '-vide-'


class GroupeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'date_creation', 'statut_groupe', 'description', 'display_profil_image',
                    'display_couverture_image', 'creator']

    list_filter = ['nom', 'date_creation', 'statut_groupe', 'creator']
    search_fields = ['nom', 'date_creation', 'statut_groupe', 'description']
    empty_value_display = '-vide-'

    def display_profil_image(self, obj):
        if obj.photo_profil.image:
            return mark_safe('<img src="{url}" width="100px" height="50px" />'.format(url=obj.photo_profil.image.url))

    def display_couverture_image(self, obj):
        if obj.photo_couverture.image:
            return mark_safe(
                '<img src="{url}" width="100px" height="50px" />'.format(url=obj.photo_couverture.image.url))


class LangueProfilAdmin(admin.ModelAdmin):
    list_display = ['profil', 'langue', 'niveau']
    list_filter = ['profil', 'langue', 'niveau']
    empty_value_display = '-vide-'


class LangueAdmin(admin.ModelAdmin):
    list_display = ['nom']
    list_filter = ['nom']
    empty_value_display = '-vide-'


class NiveauLangueAdmin(admin.ModelAdmin):
    list_display = ['niveau']
    list_filter = ['niveau']
    empty_value_display = '-vide-'


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['display_message', 'date_notification', 'profil_to_notify']
    list_filter = ['message', 'date_notification', 'profil_to_notify']
    empty_value_display = '-vide-'

    def display_message(self, obj):
        return mark_safe(obj.message)


class OffreEmploiAdmin(admin.ModelAdmin):
    list_display = ['page_entreprise', 'poste', 'nom_poste', 'profil_publicateur', 'type_emploi', 'type_contrat']
    list_filter = ['page_entreprise', 'profil_publicateur', 'type_emploi', 'type_contrat']
    empty_value_display = '-vide-'


class OrganismeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'display_logo']
    list_filter = ['nom']
    search_fields = ['nom']
    empty_value_display = '-vide-'

    def display_logo(self, obj):
        if obj.logo:
            return mark_safe('<img src="{url}" width="100px" height="50px" />'.format(url=obj.logo.url))


class PageEntrepriseAdmin(admin.ModelAdmin):
    list_display = ['nom_entreprise', 'presentation_entreprise', 'siege_social', 'annee_creation', 'specialisation',
                    'display_logo', 'display_couverture']
    list_filter = ['presentation_entreprise', 'siege_social', 'annee_creation', 'specialisation', ]
    search_fields = ['presentation_entreprise', 'siege_social', 'annee_creation', 'specialisation']
    empty_value_display = '-vide-'

    def nom_entreprise(self, obj):
        return obj.entreprise.nom

    def display_logo(self, obj):
        if obj.entreprise.logo:
            return mark_safe('<img src="{url}" width="100px" height="50px" />'.format(url=obj.entreprise.logo.url))

    def display_couverture(self, obj):
        if obj.img_couverture:
            return mark_safe('<img src="{url}" width="100px" height="50px" />'.format(url=obj.img_couverture.url))


class PosteAdmin(admin.ModelAdmin):
    list_display = ['nom_poste']
    list_filter = ['nom_poste']
    search_fields = ['nom_poste']
    empty_value_display = '-vide-'


class ReplySignalesAdmin(admin.ModelAdmin):
    list_display = ['reply_content', 'signal_sender', 'date_signale']
    list_filter = ['signal_sender', 'date_signale']
    empty_value_display = '-vide-'

    def reply_content(self, obj):
        return obj.reply.replyContent


class ReplyAdmin(admin.ModelAdmin):
    list_display = ['replyContent', 'commentaire', 'user', 'date_reply']
    list_filter = ['replyContent', 'commentaire', 'user', 'date_reply']
    empty_value_display = '-vide-'


VALID_IMAGE_EXTENSIONS = [
    "jpg",
    "jpeg",
    "png",
    "gif",
]


class ReseauSocialFileAdmin(admin.ModelAdmin):
    list_display = ['display_file', 'date_telechargement', 'profil']
    list_filter = ['profil']
    empty_value_display = '-vide-'

    def display_file(self, obj):
        extension = os.path.splitext(obj.fichier.name)[1][1:]
        if extension in VALID_IMAGE_EXTENSIONS:
            return mark_safe('<img src="{url}" width="100px" height="50px" />'.format(url=obj.fichier.url))
        else:
            return obj.fichier.name


admin.site.register(DemandeAmi, DemandeAmiAdmin)
admin.site.register(DemandeGroupe, DemandeGroupeAdmin)
admin.site.register(Conversation)
admin.site.register(MessageConversation)
admin.site.register(Groupe, GroupeAdmin)
admin.site.register(Commentaire)
admin.site.register(CommentaireSignales)
admin.site.register(StatutSignales)
admin.site.register(Statut)
admin.site.register(SharedStatut)
admin.site.register(Suivie)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(ReseauSocialFile, ReseauSocialFileAdmin)
admin.site.register(ActionBenevole, ActionsBenevoleAdmin)
admin.site.register(Ecole, EcoleAdmin)
admin.site.register(Experience, ExperienceAdmin)
admin.site.register(Formation, FormationAdmin)
admin.site.register(Langue, LangueAdmin)
admin.site.register(OffreEmploi, OffreEmploiAdmin)
admin.site.register(Organisme, OrganismeAdmin)
admin.site.register(Poste, PosteAdmin)
admin.site.register(NiveauLangue, NiveauLangueAdmin)
admin.site.register(LangueProfil, LangueProfilAdmin)
admin.site.register(PageEntreprise, PageEntrepriseAdmin)
