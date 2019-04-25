from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from main_app.models import NewsLetterMails

# Create your models here.

def admin_has_permission_model(admin, groupe, permission):
    groupe = GroupeDroit.objects.get(nom=groupe)
    droit = Droit.objects.get(nom=permission, groupe=groupe)

    if droit in admin.droits.all():
        return True
    return False




class GroupeDroit(models.Model):
    nom = models.CharField(max_length=255)
    
    def __str__(self):
        return self.nom


class Droit(models.Model):
    nom = models.CharField(max_length=255)
    groupe = models.ForeignKey(GroupeDroit, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom  +" "+ self.groupe.nom


class Admin(models.Model):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    date_creation = models.DateField()
    role = models.CharField(max_length=255,blank=True,null=True)
    image = models.ImageField(null=True,blank=True,upload_to="")
    droits = models.ManyToManyField(Droit)

    def __str__(self):
        return self.nom

    #Stats Actions
    def nombre_ajouts(self):
        return self.action_set.filter(type="Ajout").count()

    def nombre_modifications(self):
        return self.action_set.filter(type="Modification").count()

    def nombre_supressions(self):
        return self.action_set.filter(type="Suppression").count()


    # Droits Espace Admin
    def has_gerer_admins(self):
        return admin_has_permission_model(admin = self,groupe="Espace Administrateur",permission="Gérer les admins")

    def has_voir_son_profil(self):
        return admin_has_permission_model(admin=self, groupe="Espace Administrateur", permission="Voir son profil")

    def has_modifier_son_profil(self):
        return admin_has_permission_model(admin=self, groupe="Espace Administrateur", permission="Modifier son profil")

    def has_espace_admin(self):
        return self.has_gerer_admins()

    #Droits Ecommerce
    def has_ecommerce(self):
        return self.has_ecommerce_vue_ensemble() or self.has_gerer_commandes() or self.has_gerer_produits() or self.has_gerer_boutiques() or self.has_gerer_categories() or self.has_ecommerce_gerer_bannieres()

    def has_ecommerce_vue_ensemble(self):
        return admin_has_permission_model(admin=self, groupe="Ecommerce", permission="Vue d'ensemble")


    def has_gerer_commandes(self):
        return admin_has_permission_model(admin=self, groupe="Ecommerce", permission="Gérer les commandes")


    def has_gerer_produits(self):
        return admin_has_permission_model(admin=self, groupe="Ecommerce", permission="Gérer les produits")


    def has_gerer_boutiques(self):
        return admin_has_permission_model(admin=self, groupe="Ecommerce", permission="Gérer les boutiques")


    def has_gerer_categories(self):
        return admin_has_permission_model(admin=self, groupe="Ecommerce", permission="Gérer les catégories")

    def has_ecommerce_gerer_bannieres(self):
        return admin_has_permission_model(admin=self, groupe="Ecommerce", permission="Gérer les bannières et réseaux sociaux")

    def has_ecommerce_gerer_demandes_exposants(self):
        return admin_has_permission_model(admin=self, groupe="Ecommerce", permission="Gérer les demandes exposants")

    # Reseau social
    def has_reseau_social(self):
        return self.has_reseau_vue_ensemble() or self.has_reseau_groupes() or self.has_reseau_profils() or self.has_reseau_pages() or self.has_reseau_offres() or self.has_reseau_publications()

    def has_reseau_vue_ensemble(self):
        return admin_has_permission_model(admin=self, groupe="Réseau social", permission="Vue d'ensemble")

    def has_reseau_groupes(self):
        return admin_has_permission_model(admin=self, groupe="Réseau social", permission="Gérer les groupes")

    def has_reseau_profils(self):
        return admin_has_permission_model(admin=self, groupe="Réseau social", permission="Gérer les profils")

    def has_reseau_pages(self):
        return admin_has_permission_model(admin=self, groupe="Réseau social", permission="Gérer les pages entreprises")

    def has_reseau_offres(self):
        return admin_has_permission_model(admin=self, groupe="Réseau social", permission="Gérer les offres d'emploi")

    def has_reseau_publications(self):
        return admin_has_permission_model(admin=self, groupe="Réseau social", permission="Gérer les publications")

    #Journal
    def has_journal(self):
        return self.has_journal_vue_ensemble() or self.has_journal_articles() or self.has_journal_articles_videos() or self.has_journal_journalistes() or self.has_journal_signalements() or self.has_journal_bannieres()

    def has_journal_vue_ensemble(self):
        return admin_has_permission_model(admin=self, groupe="Journal", permission="Vue d'ensemble")

    def has_journal_articles(self):
        return admin_has_permission_model(admin=self, groupe="Journal", permission="Gérer les articles")

    def has_journal_articles_videos(self):
        return admin_has_permission_model(admin=self, groupe="Journal", permission="Gérer les articles vidéos")

    def has_journal_journalistes(self):
        return admin_has_permission_model(admin=self, groupe="Journal", permission="Gérer les journalistes")

    def has_journal_signalements(self):
        return admin_has_permission_model(admin=self, groupe="Journal", permission="Gérer les signalements")

    def has_journal_bannieres(self):
        return admin_has_permission_model(admin=self, groupe="Journal", permission="Gérer les bannières et réseaux sociaux")

    #Newsletter
    def has_newsletter(self):
        return self.has_newsletter_vue_ensemble() or self.has_newsletter_gerer_emails() or self.has_newsletter_gerer_compagnes()

    def has_newsletter_vue_ensemble(self):
        return admin_has_permission_model(admin=self, groupe="Newsletter", permission="Vue d'ensemble")

    def has_newsletter_gerer_emails(self):
        return admin_has_permission_model(admin=self, groupe="Newsletter", permission="Gérer les emails")

    def has_newsletter_gerer_compagnes(self):
        return admin_has_permission_model(admin=self, groupe="Newsletter", permission="Gérer les compagnes")

    # Page de garde

    def has_pagegarde(self):
        return self.has_pagegarde_vue_ensemble() or self.has_pagegarde_utilisateurs() or self.has_pagegarde_utilisateurs_blacklistes() or self.has_pagegarde_messages_contact()

    def has_pagegarde_vue_ensemble(self):
        return admin_has_permission_model(admin=self, groupe="Page de garde", permission="Vue d'ensemble")

    def has_pagegarde_utilisateurs(self):
        return admin_has_permission_model(admin=self, groupe="Page de garde", permission="Gérer les utilisateurs")

    def has_pagegarde_utilisateurs_blacklistes(self):
        return admin_has_permission_model(admin=self, groupe="Page de garde", permission="Gérer les utilisateurs blacklistés")

    def has_pagegarde_messages_contact(self):
        return admin_has_permission_model(admin=self, groupe="Page de garde", permission="Gérer les messages de contacts")

    # QA

    def has_qa(self):
        return  self.has_qa_vue_ensemble() or self.has_qa_questions() or self.has_qa_reponses() or self.has_qa_categories() or self.has_qa_experts() or self.has_qa_articles()

    def has_qa_vue_ensemble(self):
        return admin_has_permission_model(admin=self,groupe="QA", permission="Vue d'ensemble")

    def has_qa_questions(self):
        return admin_has_permission_model(admin=self, groupe="QA", permission="Gérer les questions")

    def has_qa_reponses(self):
        return admin_has_permission_model(admin=self, groupe="QA", permission="Gérer les réponses")

    def has_qa_categories(self):
        return admin_has_permission_model(admin=self, groupe="QA", permission="Gérer les catégories")

    def has_qa_experts(self):
        return admin_has_permission_model(admin=self, groupe="QA", permission="Gérer les experts")

    def has_qa_articles(self):
        return admin_has_permission_model(admin=self, groupe="QA", permission="Gérer les articles")

    # AO


    def has_ao(self):
        return  self.has_ao_vue_ensemble() or self.has_ao_profils_entreprises() or self.has_ao_lots() or self.has_ao_appels_offres() or self.has_ao_devis() or self.has_ao_parametres() or self.has_ao_utilisateurs()

    def has_ao_vue_ensemble(self):
        return admin_has_permission_model(admin=self, groupe="AO", permission="Vue d'ensemble")

    def has_ao_parametres(self):
        return admin_has_permission_model(admin=self, groupe="AO", permission="Gérer les parametres")

    def has_ao_profils_entreprises(self):
        return admin_has_permission_model(admin=self, groupe="AO", permission="Gérer les profils entreprises")

    def has_ao_utilisateurs(self):
        return admin_has_permission_model(admin=self, groupe="AO", permission="Gérer les utilisateurs")

    def has_ao_appels_offres(self):
        return admin_has_permission_model(admin=self, groupe="AO", permission="Gérer les appels d'offres")

    def has_ao_lots(self):
        return admin_has_permission_model(admin=self, groupe="AO", permission="Gérer les lots")


    def has_ao_devis(self):
        return admin_has_permission_model(admin=self, groupe="AO", permission="Gérer les devis")

    # Elearning

    def has_elearning(self):
        return self.has_elearning_vue_ensemble() or self.has_elearning_professeurs() or self.has_elearning_categories() or self.has_elearning_subcategories() or self.has_elearning_coupons() or self.has_elearning_promotions() or self.has_elearning_commandes()

    def has_elearning_vue_ensemble(self):
        return admin_has_permission_model(admin=self, groupe="Elearning", permission="Vue d'ensemble")

    def has_elearning_professeurs(self):
        return admin_has_permission_model(admin=self, groupe="Elearning", permission="Gérer les professeurs")

    def has_elearning_categories(self):
        return admin_has_permission_model(admin=self, groupe="Elearning", permission="Gérer les catégories")

    def has_elearning_subcategories(self):
        return admin_has_permission_model(admin=self, groupe="Elearning", permission="Gérer les sous catégories")

    def has_elearning_course(self):
        return admin_has_permission_model(admin=self, groupe="Elearning", permission="Gérer les cours")


    def has_elearning_coupons(self):
        return admin_has_permission_model(admin=self, groupe="Elearning", permission="Gérer les coupons")

    def has_elearning_promotions(self):
        return admin_has_permission_model(admin=self, groupe="Elearning", permission="Gérer les promotions")

    def has_elearning_commandes(self):
        return admin_has_permission_model(admin=self, groupe="Elearning", permission="Gérer les commandes")










ACTION_TYPES = (
    ('a','Ajout'),
    ('m', 'Modification'),
    ('s', 'Suppression'),
)

class Action(models.Model):
    nom = models.CharField(max_length=2555)
    date = models.DateTimeField()
    type = models.CharField(max_length=255)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)
    

    def __str__(self):
        return self.nom



class Compagne(models.Model):
    titre = models.CharField( max_length=300)
    date = models.DateField(auto_now_add=True)
    emails = models.ManyToManyField(NewsLetterMails)
    emails_ouverts = models.IntegerField(default=0)
    envoyee = models.BooleanField(default=False)
    lanceur = models.ForeignKey(Admin,on_delete=models.CASCADE)
    last_seen = models.DateTimeField(default=None,null=True)
    contenu_email = RichTextUploadingField(default="")

    def __str__(self):
        return self.titre +" par "+ self.lanceur.prenom +" "+ self.lanceur.nom


#Singleton Accessible only by static method
class Parameters(models.Model):
    langue = models.BooleanField(default=False)
    titre_site = models.CharField( max_length=300, default="Ecosysteme BTP")
    email_host = models.CharField( max_length=300, default="smtp.gmail.com")
    email_host_user = models.CharField( max_length=300,default="")
    email_host_password = models.CharField( max_length=300,default="")
    email_port = models.CharField( max_length=300,default="587")

    @staticmethod
    def get_object():
        try:
            p = Parameters.objects.first()
            if p is None:
                raise Exception
            return p
        except:
            p = Parameters.objects.create()
            return p

    @staticmethod
    def update_object(langue, email_host , email_host_user , email_host_password , email_port,titre_site):
        try:
            p = Parameters.objects.all().first()
            p.langue = langue
            p.email_host = email_host
            p.email_host_user = email_host_user
            p.email_host_password = email_host_password
            p.email_port = email_port
            p.titre_site = titre_site
            p.save()
        except:
            Parameters.objects.create()

    @staticmethod
    def get_langue_value():
        try:
            p = Parameters.objects.all().first()
            return p.langue
        except:
            p = Parameters.objects.create()
            return p.langue

    @staticmethod
    def set_langue_value(value):
        try:
            p = Parameters.objects.all().first()
            p.langue = value
            p.save()
        except:
            Parameters.objects.create()