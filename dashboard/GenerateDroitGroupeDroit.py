from dashboard.models import Droit,GroupeDroit


def GroupeDroitEspaceAministrateur():
    g = GroupeDroit()
    g.nom = "Espace Administrateur"
    g.save()


    d1 = Droit()
    d1.nom = "Gérer les admins"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Voir son profil"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Modifier son profil"
    d1.groupe = g
    d1.save()

def GroupeDroitPageDeGarde():
    g = GroupeDroit()
    g.nom = "Page de garde"
    g.save()

    d1 = Droit()
    d1.nom = "Vue d'ensemble"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les utilisateurs"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les utilisateurs blacklistés"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les messages de contacts"
    d1.groupe = g
    d1.save()


def GroupeDroitNewsLetter():
    g = GroupeDroit()
    g.nom = "Newsletter"
    g.save()

    d1 = Droit()
    d1.nom = "Vue d'ensemble"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les emails"  # Voir la liste de mails + lancer une compagne
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les compagnes" #Voir la liste de mails + lancer une compagne
    d1.groupe = g
    d1.save()



def GroupeDroitRéseausocial():
    g = GroupeDroit()
    g.nom = "Réseau social"
    g.save()

    d1 = Droit()
    d1.nom = "Vue d'ensemble"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les groupes"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les profils"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les pages entreprises"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les offres d'emploi"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les publications"
    d1.groupe = g
    d1.save()


def GroupeDroitJournal():
    g = GroupeDroit()
    g.nom = "Journal"
    g.save()

    d1 = Droit()
    d1.nom = "Vue d'ensemble"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les articles"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les articles vidéos"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les journalistes"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les signalements"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les bannières et réseaux sociaux"
    d1.groupe = g
    d1.save()


def GroupeDroitEcommerce():
    g = GroupeDroit()
    g.nom = "Ecommerce"
    g.save()

    d1 = Droit()
    d1.nom = "Vue d'ensemble"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les commandes"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les demandes exposants"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les produits"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les boutiques"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les catégories"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les bannières et réseaux sociaux"
    d1.groupe = g
    d1.save()


def GroupeDroitQA():
    g = GroupeDroit()
    g.nom = "QA"
    g.save()

    d1 = Droit()
    d1.nom = "Vue d'ensemble"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les questions"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les réponses"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les catégories"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les experts"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les articles"
    d1.groupe = g
    d1.save()


def GroupeDroitAO():
    g = GroupeDroit()
    g.nom = "AO"
    g.save()

    d1 = Droit()
    d1.nom = "Vue d'ensemble"
    d1.groupe = g
    d1.save()


    d1 = Droit()
    d1.nom = "Gérer les profils entreprises"
    d1.groupe = g
    d1.save()


    d1 = Droit()
    d1.nom = "Gérer les lots"
    d1.groupe = g
    d1.save()


    d1 = Droit()
    d1.nom = "Gérer les appels d'offres"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les devis"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les parametres"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les utilisateurs"
    d1.groupe = g
    d1.save()


def GroupeDroitElearning():
    g = GroupeDroit()
    g.nom = "Elearning"
    g.save()

    d1 = Droit()
    d1.nom = "Vue d'ensemble"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les professeurs"
    d1.groupe = g
    d1.save()


    d1 = Droit()
    d1.nom = "Gérer les catégories"
    d1.groupe = g
    d1.save()


    d1 = Droit()
    d1.nom = "Gérer les sous catégories"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les cours"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les coupons"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les promotions"
    d1.groupe = g
    d1.save()

    d1 = Droit()
    d1.nom = "Gérer les commandes"
    d1.groupe = g
    d1.save()


def generate_droits():
    # A executer sur une view
    GroupeDroitEspaceAministrateur()
    GroupeDroitEcommerce()
    GroupeDroitJournal()
    GroupeDroitNewsLetter()
    GroupeDroitPageDeGarde()
    GroupeDroitRéseausocial()
    GroupeDroitQA()
    GroupeDroitAO()
    GroupeDroitElearning()
