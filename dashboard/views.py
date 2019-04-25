from django.core import mail
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.shortcuts import render, HttpResponse, Http404, redirect, get_object_or_404
from django.urls import reverse
from django.template.loader import render_to_string
from tracking_analyzer.models import Tracker
import json
from ecommerce.models import *
from journal.models import *
from SocialMedia.models import *
from main_app.SendMailBackend import get_custom_connection
from main_app.models import Image as main_Image, Profil, Contact, Entreprise
from qa.models import Question, Answer as QA_Answer, Category as QA_Category, Article as QA_Article, \
    SignalAnswer as QA_SignalAnswer, SignalArticle as QA_SignalArticle, SignalComment as QA_SignalComment, \
    SignalQuestion as QA_SignalQuestion, Comment as QA_Comment
from eLearning.models import Category as  Elearning_Category, Question as Elearning_Question, \
    Answer as  Elearning_Answer, Cart   as Elearning_Cart, Chapter  as Elearning_Chapter, Coupon  as Elearning_Coupon, Course  as Elearning_Course, Exam  as Elearning_Exam, Order as Elearning_Order, \
    OrderLine as Elearning_OrderLine, Formation as Elearning_Formation, Prerequisites  as Elearning_Prerequisites, \
    PostSkills  as Elearning_PostSkills, Sale as Elearning_Sale, SubCategory  as Elearning_SubCategory,Part as Elearning_Part

from django.http import JsonResponse
from .dynamic_classes import Boutique
from django.contrib import messages
from .models import *
from .decorators import *
from .forms import *
from django.contrib.auth.hashers import check_password
from django.utils.html import strip_tags
from django.conf import settings
from PIL import Image as Image_PIL
from django.db.models import Avg, Count, Min, Sum, Q, F, Subquery, OuterRef
from django.utils.dateformat import DateFormat
from django.db.models.functions import ExtractMonth
from datetime import datetime, timedelta
import datetime as datetimee
import operator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.views.decorators.http import require_POST

from django.contrib.gis.geoip2 import GeoIP2

from ao.services import send_multiple_mails

from .GenerateDroitGroupeDroit import *


# reverse('admin:app_list', kwargs={'app_label': 'auth'})

# Create your views here.

############################### Acceuil / Login / Vue d'ensemble principale ###############################

def index(request):
    if request.method == "POST":
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)

        if email is None or password is None:
            messages.error(request, "Veuillez renseigner tous les champs.")
            return render(request, 'dashboard/login.html')
        else:
            admin = get_object_or_none(Admin, email__iexact=email)

            # Si le mail n'existe pas
            if admin is None:
                messages.error(request, "L'e-mail ou le mot de passe est incorrecte.")
                return render(request, 'dashboard/login.html')
            # Si le mail existe mais le mdp n'est pas correcte
            if not check_password(password, admin.password):
                messages.error(request, "L'e-mail ou le mot de passe est incorrecte.")
                return render(request, 'dashboard/login.html')
            else:  # Si tout est OK.
                request.session['id_admin'] = admin.id

    id_admin = request.session.get('id_admin', None)

    if id_admin is None:
        return render(request, 'dashboard/login.html')
    else:
        context = {}

        context['commandes'] = Order.objects.all().count()
        context['articles'] = News.objects.all().count()
        context['non_lus'] = Contact.objects.filter(lu=False).count()
        context['utilisateurs'] = Profil.objects.all().count()

        context['produits'] = Product.objects.all().count()
        context['questions'] = Question.objects.all().count()
        context['reponses'] = QA_Answer.objects.all().count()
        context['nb_appels_offres'] = AO.objects.all().count()
        # context['cours'] = QA_Answer.objects.all().count()

        return render(request, 'dashboard/vue_ensemble.html', context)


def logout(request):
    del request.session['id_admin']
    return redirect('dashboard:index')


############################# Tracking ###############################

def tracking_visites(request):
    context = {}

    page = request.GET.get('page', 1)

    type = request.GET.get('type', None)
    url = request.GET.get('url', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    email = request.GET.get('email', None)

    print(email)
    try:
        user = User.objects.get(email=email)
    except:
        user = None

    tracking_data = Tracker.objects.exclude(device_type__icontains="bot")

    if type or url or start_date or end_date or user:
        tracking_data = Tracker.objects.all()

        print(tracking_data.count())

        if type:
            tracking_data = tracking_data.filter(model_name=type)
        if start_date and end_date:
            end_date_splited = end_date.split("-")
            end_date_year = int(end_date_splited[0])
            end_date_month = int(end_date_splited[1])
            end_date_day = int(end_date_splited[2])

            start_date_splited = start_date.split("-")
            start_date_year = int(start_date_splited[0])
            start_date_month = int(start_date_splited[1])
            start_date_day = int(start_date_splited[2])

            tracking_data = tracking_data.filter(
                timestamp__gte=datetimee.date(start_date_year, start_date_month, start_date_day),
                timestamp__lte=(datetimee.date(end_date_year, end_date_month, end_date_day) + timedelta(days=1)))
        if url:
            ids = []
            trouve = 0
            for tracking in tracking_data:
                if tracking.content_object:
                    if url.lower() == tracking.content_object.tracking_get_absolute_url().lower():
                        ids.append(tracking.id)
                        trouve = 1

            if trouve == 0:
                tracking_data = tracking_data.none()
            else:
                tracking_data = tracking_data.filter(id__in=ids)
        if user:
            tracking_data = tracking_data.filter(user=user)
        tracking_data = tracking_data.order_by('-timestamp')
    else:
        tracking_data = Tracker.objects.all().order_by('-timestamp')

    # tracking_data = Tracker.objects.all().order_by('-timestamp')

    paginator = Paginator(tracking_data, 10)

    try:
        tracking_list = paginator.page(page)
    except PageNotAnInteger:
        tracking_list = paginator.page(1)
    except EmptyPage:
        tracking_list = paginator.page(paginator.num_pages)

    context['tracking_list'] = tracking_list

    return render(request, 'dashboard/tracking/visites.html', context)


def tracking_visite(request, id_visite):
    tracking = get_object_or_404(Tracker, id=id_visite)

    context = dict()

    context['tracking'] = tracking
    context['tracking_list_user'] = Tracker.objects.filter(user=tracking.user).order_by('-timestamp')[:30]

    g = GeoIP2()

    try:
        city = g.city(tracking.ip_address)  # city.latitude, city.longitude, city.country_name
    except:
        city = None

    context['city'] = city

    return render(request, 'dashboard/tracking/visite.html', context)


############################### Espace Administrateurs ###############################


def admin_admins_list(request):
    if not admin_has_permission(groupe="Espace Administrateur", permission="Gérer les admins", request=request):
        return redirect("dashboard:index")

    context = {}

    context['admins'] = Admin.objects.all()  # .exclude(id=request.session['id_admin'])

    return render(request, 'dashboard/admin/admins_list.html', context)


def delete_admins(request):
    if not admin_has_permission(groupe="Espace Administrateur", permission="Gérer les admins", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun administrateur n\'est sélectionné.'})
    else:
        for id in ids:
            admin_to_delete = Admin.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé l'administrateur <strong>" + admin_to_delete.nom.title() + " " + admin_to_delete.prenom.title() + " </strong>"
            action.save()

            admin_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les administrateurs sélectionnés ont été supprimés.'})


def admin_add_admin(request):
    if not admin_has_permission(groupe="Espace Administrateur", permission="Gérer les admins", request=request):
        return redirect("dashboard:index")

    context = {}

    if request.method == "POST":
        admin_form = FormAdminAjout(request.POST, request.FILES)

        droits_administration = request.POST.getlist('droits_administration')
        droits_page_de_garde = request.POST.getlist('droits_page_de_garde')
        droits_newsletter = request.POST.getlist('droits_newsletter')
        droits_reseau_social = request.POST.getlist('droits_reseau_social')
        droits_journal = request.POST.getlist('droits_journal')
        droits_ecommerce = request.POST.getlist('droits_ecommerce')
        droits_qa = request.POST.getlist('droits_qa')
        droits_ao = request.POST.getlist('droits_ao')
        droits_elearning = request.POST.getlist('droits_elearning')

        droits_selected = droits_administration + droits_page_de_garde + droits_newsletter + droits_reseau_social + droits_journal + droits_ecommerce + droits_qa + droits_ao + droits_elearning

        if admin_form.is_valid() and len(droits_selected) > 0:
            droits_to_add = list(Droit.objects.filter(id__in=droits_selected))
            admin = admin_form.save(commit=False)
            admin.date_creation = timezone.now()
            admin.password = make_password(admin.password)
            admin.save()
            admin.droits.add(*droits_to_add)

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Ajout"
            action.nom = "A ajouté l'administrateur <strong>" + admin.nom.title() + " " + admin.prenom.title() + "</strong>"
            action.save()

            messages.success(request, "L'administrateur a été ajouté avec succès.")
            return redirect('dashboard:admin_admins_list')

        elif len(droits_selected) == 0:
            context['form_add_admin_droits_error'] = "Vous devez au moins choisir un droit."
            context['form_add_admin'] = admin_form
        else:
            print(admin_form.errors)
            context['form_add_admin'] = admin_form
    else:
        context['form_add_admin'] = FormAdminAjout()

    context['droits_administration'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Espace Administrateur"))
    context['droits_page_de_garde'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Page de garde"))
    context['droits_newsletter'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Newsletter"))
    context['droits_reseau_social'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Réseau social"))
    context['droits_journal'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Journal"))
    context['droits_ecommerce'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Ecommerce"))

    context['droits_qa'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="QA"))
    context['droits_ao'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="AO"))
    context['droits_elearning'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Elearning"))

    return render(request, 'dashboard/admin/add_admin.html', context)


def delete_admin(request, id_admin):
    admin_profil = get_object_or_none(Admin, id=id_admin)

    context = {}

    if (not admin_has_permission(groupe="Espace Administrateur", permission="Gérer les admins",
                                 request=request) and admin_profil.id is not admin_logged(request).id) or (
            (not admin_has_permission(groupe="Espace Administrateur", permission="Modifier son profil",
                                      request=request)) and admin_profil.id is admin_logged(
        request).id) or admin_profil is None:
        return redirect("dashboard:index")

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Modification"
    action.nom = "A modifié l'administrateur <strong>" + admin_profil.nom.title() + " " + admin_profil.prenom.title() + "</strong>"
    action.save()

    admin_profil.delete()

    messages.success(request, "L'administrateur a été supprimé avec succès.")

    return redirect('dashboard:admin_admins_list')


def update_admin(request, id_admin):
    admin_update = get_object_or_none(Admin, id=id_admin)

    context = {}

    if (not admin_has_permission(groupe="Espace Administrateur", permission="Gérer les admins",
                                 request=request) and admin_update.id is not admin_logged(request).id) or (
            (not admin_has_permission(groupe="Espace Administrateur", permission="Modifier son profil",
                                      request=request)) and admin_update.id is admin_logged(
        request).id) or admin_update is None:
        return redirect("dashboard:index")

    context['admin_update'] = admin_update

    context['form_add_admin'] = FormAdminModification(instance=admin_update)
    context['form_update_password'] = FormAdminModifierPassword(instance=admin_update)

    context['droits_administration'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Espace Administrateur"))
    context['droits_page_de_garde'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Page de garde"))
    context['droits_newsletter'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Newsletter"))
    context['droits_reseau_social'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Réseau social"))
    context['droits_journal'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Journal"))
    context['droits_ecommerce'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Ecommerce"))
    context['droits_qa'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="QA"))
    context['droits_ao'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="AO"))
    context['droits_elearning'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Elearning"))

    return render(request, 'dashboard/admin/update_admin.html', context)


def update_admin_informations(request, id_admin):
    admin_update = get_object_or_none(Admin, id=id_admin)

    context = {}

    if (not admin_has_permission(groupe="Espace Administrateur", permission="Gérer les admins",
                                 request=request) and admin_update.id is not admin_logged(request).id) or (
            (not admin_has_permission(groupe="Espace Administrateur", permission="Modifier son profil",
                                      request=request)) and admin_update.id is admin_logged(
        request).id) or admin_update is None:
        return redirect("dashboard:index")

    if request.method == "POST":
        admin_form = FormAdminModification(request.POST, request.FILES, instance=admin_update)

        droits_administration = request.POST.getlist('droits_administration')
        droits_page_de_garde = request.POST.getlist('droits_page_de_garde')
        droits_newsletter = request.POST.getlist('droits_newsletter')
        droits_reseau_social = request.POST.getlist('droits_reseau_social')
        droits_journal = request.POST.getlist('droits_journal')
        droits_ecommerce = request.POST.getlist('droits_ecommerce')
        droits_qa = request.POST.getlist('droits_qa')
        droits_ao = request.POST.getlist('droits_ao')
        droits_elearning = request.POST.getlist('droits_elearning')

        droits_selected = droits_administration + droits_page_de_garde + droits_newsletter + droits_reseau_social + droits_journal + droits_ecommerce + droits_qa + droits_ao + droits_elearning

        if admin_form.is_valid() and len(droits_selected) > 0:
            droits_to_add = list(Droit.objects.filter(id__in=droits_selected))
            admin = admin_form.save(commit=False)
            admin.droits.clear()
            admin.droits.add(*droits_to_add)
            admin.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié l'administrateur <strong>" + admin.nom.title() + " " + admin.prenom.title() + "</strong>"
            action.save()

            messages.success(request, "L'administrateur a été modifié avec succès.")
            return redirect('dashboard:admin_admins_list')

        elif len(droits_selected) == 0:
            context['form_add_admin_droits_error'] = "Vous devez au moins choisir un droit."
            context['form_add_admin'] = admin_form
        else:
            print(admin_form.errors)
            context['form_add_admin'] = admin_form
    else:
        context['form_add_admin'] = FormAdminModification(instance=admin_update)

    context['droits_administration'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Espace Administrateur"))
    context['droits_page_de_garde'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Page de garde"))
    context['droits_newsletter'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Newsletter"))
    context['droits_reseau_social'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Réseau social"))
    context['droits_journal'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Journal"))
    context['droits_ecommerce'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Ecommerce"))
    context['droits_qa'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="QA"))
    context['droits_ao'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="AO"))
    context['droits_elearning'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Elearning"))

    return render(request, 'dashboard/admin/update_admin.html', context)

    context['form_update_password'] = FormAdminModifierPassword(instance=admin_update)


def update_admin_password(request, id_admin):
    admin_update = get_object_or_none(Admin, id=id_admin)

    context = {}

    if (not admin_has_permission(groupe="Espace Administrateur", permission="Gérer les admins",
                                 request=request) and admin_update.id is not admin_logged(request).id) or (
            (not admin_has_permission(groupe="Espace Administrateur", permission="Modifier son profil",
                                      request=request)) and admin_update.id is admin_logged(
        request).id) or admin_update is None:
        return redirect("dashboard:index")

    context['admin_update'] = admin_update
    context['form_add_admin'] = FormAdminModification(instance=admin_update)

    if request.method == "POST":
        form_modifier_password = FormAdminModifierPassword(request.POST, instance=admin_update)

        if form_modifier_password.is_valid():
            admin = form_modifier_password.save(commit=False)
            admin.password = make_password(admin.password)
            admin.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié l'administrateur <strong>" + admin.nom.title() + " " + admin.prenom.title() + "</strong>"
            action.save()

            messages.success(request, "L'administrateur a été modifié avec succès.")
            return redirect('dashboard:admin_admins_list')


        else:
            context['form_update_password'] = form_modifier_password
    else:
        context['form_update_password'] = FormAdminModifierPassword()

    context['droits_administration'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Espace Administrateur"))
    context['droits_page_de_garde'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Page de garde"))
    context['droits_newsletter'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Newsletter"))
    context['droits_reseau_social'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Réseau social"))
    context['droits_journal'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Journal"))
    context['droits_ecommerce'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Ecommerce"))

    return render(request, 'dashboard/admin/update_admin.html', context)


def admin_profile(request, id_admin):
    admin_profil = get_object_or_404(Admin, id=id_admin)

    context = {}

    if (not admin_has_permission(groupe="Espace Administrateur", permission="Gérer les admins",
                                 request=request) and admin_profil.id is not admin_logged(request).id) or (
            (not admin_has_permission(groupe="Espace Administrateur", permission="Voir son profil",
                                      request=request)) and admin_profil.id is admin_logged(
        request).id) or admin_profil is None:
        print((admin_has_permission(groupe="Espace Administrateur", permission="Voir son profil",
                                    request=request)) and admin_profil.id is admin_logged(request).id)

        return redirect("dashboard:index")

    elif admin_profil.id is admin_logged(request).id:
        context['myprofil'] = True
    # Si c'est lui meme on le redirige vers myprofil

    context['admin_profil'] = admin_profil

    context['droits_administration'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Espace Administrateur"))
    context['droits_page_de_garde'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Page de garde"))
    context['droits_newsletter'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Newsletter"))
    context['droits_reseau_social'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Réseau social"))
    context['droits_journal'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Journal"))
    context['droits_ecommerce'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Ecommerce"))
    context['droits_qa'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="QA"))
    context['droits_ao'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="AO"))
    context['droits_elearning'] = Droit.objects.filter(groupe=GroupeDroit.objects.get(nom="Elearning"))

    context['actions'] = Action.objects.filter(admin=admin_profil).order_by('-date')

    return render(request, 'dashboard/admin/admin_profile.html', context)


##End Espace Administrateurs


##Page de garde


# Vue Generale

def page_garde_general_view(request):
    if not admin_has_permission(permission="Vue d'ensemble", groupe="Page de garde", request=request):
        return redirect("dashboard:index")

    inscrits = Profil.objects.all()
    messages = Contact.objects.all()

    # ces 7 derniers mois
    last_seven_months = datetime.today() - timedelta(days=220)  # last 220 days
    #
    abonnees_per_month = inscrits.filter(user__date_joined__gte=last_seven_months).annotate(
        month=ExtractMonth('user__date_joined')).values('month').annotate(total_abonnees=Count('id')).order_by()

    context = {}

    context['inscrits'] = inscrits
    context['messages_non_lu'] = messages.filter(lu=False)
    context['blacklisted'] = inscrits.filter(blacklisted=True)
    context['inscrits_per_type_per_month'] = abonnees_per_month
    context['professionals'] = inscrits.filter(is_professional=True).count()
    context['etudiants'] = inscrits.filter(is_etudiant=True).count()
    context['journalistes'] = inscrits.filter(is_journaliste=True).count()
    context['particuliers'] = inscrits.filter(is_particulier=True).count()

    return render(request, 'dashboard/page_garde/vue_generale.html', context)


# Utilisateurs

def users_list(request):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    context = {}

    context['profils'] = Profil.objects.all()

    return render(request, 'dashboard/page_garde/lists/liste_utilisateurs.html', context)


def user_infos(request, id_user):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    profil = get_object_or_404(Profil, id=id_user)
    journaliste = get_object_or_none(Journalist, email=profil.user.email)
    if journaliste is None:
        articles = []
    else:
        articles = journaliste.news_set.all()

    context = {}

    context['profil'] = profil
    context['exist_newsletter'] = NewsLetterMails.objects.filter(email=profil.user.email).count()
    context['followers'] = Suivie.objects.filter(followed_profil=profil).count()

    context['articles'] = articles

    context['tracking_dernieres_visites'] = Tracker.objects.filter(user=context['profil'].user).order_by(
        '-timestamp')[:10]

    return render(request, 'dashboard/page_garde/infos/infos_user.html', context)


def delete_user(request, id_user):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    profil = get_object_or_404(Profil, id=id_user)

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Suppression"
    action.nom = "A supprimé l'utilisateur <strong>" + profil.user.first_name.title() + " " + profil.user.last_name.title() + "</strong>"
    action.save()

    profil.user.delete()
    profil.delete()

    messages.success(request,
                     "L'utilisateur " + profil.user.first_name.title() + " " + profil.user.last_name.title() + " a été supprimé ")

    return redirect('dashboard:users_list')


def update_user(request, id_user):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    profil = get_object_or_404(Profil, id=id_user)

    context = {}

    context['form'] = FormModifierProfilGarde(instance=profil)
    context['form_user'] = FormModifierUserGarde(instance=profil.user)
    context['form_image_profil'] = FormModifierMainImage(instance=profil.photo_profil)
    context['form_image_couverture'] = FormModifierMainImage(instance=profil.photo_couverture)
    context['form_update_password'] = FormAdminModifierUserPassword(instance=profil.user)
    context['profil'] = profil

    return render(request, 'dashboard/page_garde/modification/update_user.html', context)


def update_user_password(request, id_profil):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    profil = get_object_or_none(Profil, id=id_profil)

    context = {}

    if request.method == "POST":
        form_modifier_password = FormAdminModifierUserPassword(request.POST, instance=profil.user)

        if form_modifier_password.is_valid():
            user = form_modifier_password.save(commit=False)
            user.password = make_password(user.password)
            user.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié l'administrateur <strong>" + user.first_name.title() + " " + user.last_name.title() + "</strong>"
            action.save()

            messages.success(request, "L'utilisateur a été modifié avec succès.")
            return redirect('dashboard:update_user', id_user=id_profil)
        else:
            messages.error(request, form_modifier_password.errors)
            context['form_update_password'] = form_modifier_password

    return redirect('dashboard:update_user', id_profil)


def main_update_profile_pic(request, id_user):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    profil = Profil.objects.get(id=id_user)

    if request.method == "POST":

        form = FormModifierMainImage(request.POST, request.FILES)

        if form.is_valid():
            print("valid")
            image = form.save()
            profil.photo_profil = image
            profil.save()
            messages.success(request, "L'image de profil a été modifiée avec succès.")
        else:
            print("no valid")
            print(form.errors)

    return redirect('dashboard:update_user', profil.id)


def main_update_cover_pic(request, id_user):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    profil = Profil.objects.get(id=id_user)

    if request.method == "POST":

        form = FormModifierMainImage(request.POST, request.FILES)

        if form.is_valid():
            image = form.save()
            profil.photo_couverture = image
            profil.save()
            messages.success(request, "L'image de couverture a été modifiée avec succès.")
        else:
            print(form.errors)

    return redirect('dashboard:update_user', profil.id)


def update_user_infos(request, id_user):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    profil = get_object_or_404(Profil, id=id_user)

    context = {}

    if request.method == "POST":
        form = FormModifierProfilGarde(request.POST, instance=profil)
        form_user = FormModifierUserGarde(request.POST, instance=profil.user)
        if form.is_valid() and form_user.is_valid():
            form.save()
            form_user.save()
            messages.success(request, "Le profil a été modifié avec succès.")
        else:
            print(form.errors)

    return redirect('dashboard:update_user', id_user)


# Utilisateurs ajax
def delete_users(request):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun utilisateur sélectionné.'})
    else:
        for id in ids:
            profil = Profil.objects.get(id=id)
            user = profil.user

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé l'utilisateur <strong>" + user.first_name + " " + user.last_name + "</strong> email : <strong>" + user.email + "</strong>"
            action.save()

            print("profils = " + str(profil.delete()))
            user.delete()

        return JsonResponse({'status': 'success', 'message': 'Les utilisateurs sélectionnés ont été supprimés.'})


def verify_users(request):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun utilisateur sélectionné.'})
    else:
        for id in ids:
            profils_to_delete = Profil.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A marqué comme vérifié <strong>" + profils_to_delete.user.first_name + " " + profils_to_delete.user.last_name + "</strong> email : <strong>" + profils_to_delete.user.email + "</strong>"
            action.save()

            profils_to_delete.user.is_active = True
            profils_to_delete.user.save()

        return JsonResponse({'status': 'success', 'message': 'Les utilisateurs sélectionnés ont été vérifiés.'})


def deverify_users(request):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun utilisateur sélectionné.'})
    else:
        for id in ids:
            profils_to_delete = Profil.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A marqué comme non vérifié l'utilisateur <strong>" + profils_to_delete.user.first_name + " " + profils_to_delete.user.last_name + "</strong> email : <strong>" + profils_to_delete.user.email + "</strong>"
            action.save()

            profils_to_delete.user.is_active = False
            profils_to_delete.user.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Les utilisateurs sélectionnés ont été marqué comme non vérifiés.'})


def activate_users(request):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun utilisateur sélectionné.'})
    else:
        for id in ids:
            profils_to_delete = Profil.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A marqué comme activé <strong>" + profils_to_delete.user.first_name + " " + profils_to_delete.user.last_name + "</strong> email : <strong>" + profils_to_delete.user.email + "</strong>"
            action.save()

            profils_to_delete.is_active_professional = True
            profils_to_delete.save()

        return JsonResponse({'status': 'success', 'message': 'Les utilisateurs sélectionnés ont été activés.'})


def desactivate_users(request):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun utilisateur sélectionné.'})
    else:
        for id in ids:
            profils_to_delete = Profil.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A marqué comme non activé l'utilisateur <strong>" + profils_to_delete.user.first_name + " " + profils_to_delete.user.last_name + "</strong> email : <strong>" + profils_to_delete.user.email + "</strong>"
            action.save()

            profils_to_delete.is_active_professional = False
            profils_to_delete.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Les utilisateurs sélectionnés ont été marqué comme non activés.'})


def blacklist_users(request):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun utilisateur sélectionné.'})
    else:
        for id in ids:
            profils_to_delete = Profil.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A marqué comme blacklisté <strong>" + profils_to_delete.user.first_name + " " + profils_to_delete.user.last_name + "</strong> email : <strong>" + profils_to_delete.user.email + "</strong>"
            action.save()

            profils_to_delete.blacklisted = True
            profils_to_delete.save()

        return JsonResponse({'status': 'success', 'message': 'Les utilisateurs sélectionnés ont été blacklistés.'})


def deblacklist_users(request):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun utilisateur sélectionné.'})
    else:
        for id in ids:
            profils_to_delete = Profil.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A marqué comme non blacklisté l'utilisateur <strong>" + profils_to_delete.user.first_name + " " + profils_to_delete.user.last_name + "</strong> email : <strong>" + profils_to_delete.user.email + "</strong>"
            action.save()

            profils_to_delete.blacklisted = False
            profils_to_delete.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Les utilisateurs sélectionnés ont été marqué comme non blacklistés.'})


## Blacklisted Utilisateurs

def blacklisted_users_list(request):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    context = {}

    context['profils'] = Profil.objects.filter(blacklisted=True)

    return render(request, 'dashboard/page_garde/lists/liste_utilisateurs_blacklistes.html', context)


# Messages

def main_messages(request):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les messages de contacts", request=request):
        return redirect("dashboard:index")

    context = {}

    context['messages'] = Contact.objects.all()

    return render(request, 'dashboard/page_garde/contact_us/contact_messages.html', context)


# Ajax
def delete_messages(request):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les messages de contacts", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun message sélectionné.'})
    else:
        for id in ids:
            message_to_delete = Contact.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé le message de contactez-nous <strong>" + message_to_delete.message[
                                                                              30:] + "</strong> de la part de <strong>" + message_to_delete.full_name + "</strong>"
            action.save()

            message_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les messages sélectionnés ont été supprimés.'})


def vue_message(request, id_message):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les messages de contacts", request=request):
        return redirect("dashboard:index")

    message = get_object_or_404(Contact, id=id_message)

    message.lu = True
    message.save()

    context = {}

    context['message'] = message
    context['form_message'] = FormRepondreMessageContact()

    return render(request, 'dashboard/page_garde/contact_us/contact_message.html', context)


def repondre_message(request, id_message):
    if not admin_has_permission(groupe="Page de garde", permission="Gérer les messages de contacts", request=request):
        return redirect("dashboard:index")

    if request.method == "POST":

        message = get_object_or_404(Contact, id=id_message)

        form_message = FormRepondreMessageContact(request.POST, instance=message)
        if not form_message.is_valid():
            print(form_message.errors)
            context = {}
            context['message'] = message
            context['form_message'] = form_message
            return render(request, 'dashboard/page_garde/contact_us/contact_message.html', context)
        else:
            form_message.save(commit=False)
            message.repondu = True
            message.save()

            # send mails

            connection = get_custom_connection()  # Use default email connection

            # Manually open the connection
            connection.open()

            emails_list = []

            email_contenu_without_link = message.reponse

            # Original : src="media/...."
            # New : src="http://ecosysteme-btp.ma/media..."
            contenu_mail = email_contenu_without_link.replace('src="',
                                                              'src="' + request.scheme + "://" + request.META[
                                                                  'HTTP_HOST'] + '')
            # In production we have :
            # src = "/home/ubuntu/FINALESPR/http://ecosysteme-btp.ma/media...."
            # we replace it by
            # src="http://ecosysteme-btp.ma/media..."
            contenu_mail = contenu_mail.replace(settings.MEDIA_ROOT, "")

            email_to_send = EmailMultiAlternatives(
                "RE: " + message.sujet,
                contenu_mail,
                'Ecosysteme-BTP@gmail.com',
                [message.email, ],
            )

            email_to_send.attach_alternative(contenu_mail, "text/html")
            emails_list.append(email_to_send)

            # Send all emails in a single call -
            connection.send_messages(emails_list)
            # The connection was already open so send_messages() doesn't close it.
            # We need to manually close the connection.
            connection.close()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Ajout"
            action.nom = "A répondu au message de contact <strong>" + message.sujet + "</strong> de l'utilisateur <strong>" + message.full_name + "</strong>"
            action.save()

            messages.success(request,
                             "La réponse au message a été envoyée.")

            return redirect('dashboard:main_messages')

    else:
        raise Http404


##End Page de garde


##Newsletter
# Vue Generale
def newsletter(request):
    if not admin_has_permission(groupe="Newsletter", permission="Vue d'ensemble", request=request):
        return redirect("dashboard:index")

    context = {}

    # Ventes ces 7 derniers mois
    last_seven_months = datetime.today() - timedelta(days=220)  # last 220 days

    emails = NewsLetterMails.objects.all()
    compagnes = Compagne.objects.all()
    emails_envoyes = compagnes.aggregate(total_envoyes=Count('emails'))['total_envoyes']
    emails_ouverts = compagnes.aggregate(total_ouverts=Sum('emails_ouverts'))['total_ouverts']
    abonnees_per_month = emails.filter(date__gte=last_seven_months).annotate(month=ExtractMonth('date')).values(
        'month').annotate(total_abonnees=Count('id')).order_by()

    # Date Range 7 days for nouveau inscrits
    enddate = datetime.today()
    startdate = enddate - timedelta(days=7)

    context['compagnes'] = compagnes
    context['emails'] = emails
    context['emails_envoyes'] = emails_envoyes
    context['emails_ouverts'] = emails_ouverts if emails_ouverts else 0
    context['nouveaux_inscrits'] = emails.filter(date__range=[startdate, enddate]).count()
    context['abonnees_per_month'] = abonnees_per_month

    return render(request, 'dashboard/newsletter/vue_generale.html', context)


# Emails
def emails_list(request):
    if not admin_has_permission(groupe="Newsletter", permission="Gérer les emails", request=request):
        return redirect("dashboard:index")

    context = {}

    context['emails'] = NewsLetterMails.objects.all()
    return render(request, 'dashboard/newsletter/liste_emails.html', context)


# Ajax
def delete_emails(request):
    if not admin_has_permission(groupe="Newsletter", permission="Gérer les emails", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun email sélectionné.'})
    else:
        for id in ids:
            email_to_delete = NewsLetterMails.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé l'email de Newsletter <strong>" + email_to_delete.email + "</strong>"
            action.save()

            email_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les emails sélectionnés ont été supprimés.'})


def compagnes(request):
    if not admin_has_permission(groupe="Newsletter", permission="Gérer les compagnes", request=request):
        return redirect("dashboard:index")

    context = {}

    emails_ouverts = Compagne.objects.aggregate(Sum('emails_ouverts'))['emails_ouverts__sum']

    context['compagnes'] = Compagne.objects.all()
    context['emails_ouverts'] = emails_ouverts if emails_ouverts else 0
    context['emails_envoyes'] = Compagne.objects.aggregate(Count('emails'))['emails__count']
    try:
        context['emails_vus'] = (context['emails_ouverts'] / context['emails_envoyes']) * 100
    except:
        context['emails_vus'] = 0

    return render(request, 'dashboard/newsletter/compagnes.html', context)


# Ajax delete multi compagnes
def delete_compagnes(request):
    if not admin_has_permission(groupe="Newsletter", permission="Gérer les compagnes", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune compagne sélectionneé.'})
    else:
        for id in ids:
            compagne_to_delete = Compagne.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé la compagne de Newsletter <strong>" + compagne_to_delete.titre + "</strong>"
            action.save()

            compagne_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les compagne sélectionneés ont été supprimées.'})


# Delete on compagne
def delete_compagne(request, id_compagne):
    if not admin_has_permission(groupe="Newsletter", permission="Gérer les compagnes", request=request):
        return redirect("dashboard:index")

    compagne = get_object_or_404(Compagne, id=id_compagne)
    # if compagne.envoyee:
    #    raise Http404

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Suppression"
    action.nom = "A supprimé la compagne de Newsletter <strong>" + compagne.titre + "</strong>"
    action.save()

    compagne.delete()

    messages.success(request,
                     "La compagne " + compagne.titre + " a été supprimée ")

    return redirect('dashboard:compagnes')


# Delete on compagne
def add_email(request):
    if not admin_has_permission(groupe="Newsletter", permission="Gérer les emails", request=request):
        return redirect("dashboard:index")

    email = request.GET.get('email', None)
    type = request.GET.get('type', None)

    if not email or not type:
        return JsonResponse({'status': 'error', 'message': 'L\'email ou le type donné n\'est pas valide.'})

    if get_object_or_none(NewsLetterMails, email=email) is not None:
        return JsonResponse({'status': 'error', 'message': 'L\'email donné existe déjà  '})

    newsletteremail = NewsLetterMails()
    newsletteremail.email = email
    newsletteremail.type = type
    newsletteremail.date = timezone.now()
    newsletteremail.save()

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Ajout"
    action.nom = "A ajouté l'email <strong>" + newsletteremail.email + "</strong> à la Newsletter"
    action.save()

    return JsonResponse({'status': 'success', 'message': 'Email ajouté avec succès.', 'id': newsletteremail.id,
                         'date': DateFormat(newsletteremail.date).format('d/m/Y')})


# Lancer Compagne
# New Step 1
def lancer_compagne_new(request):
    if not admin_has_permission(groupe="Newsletter", permission="Gérer les compagnes", request=request):
        return redirect("dashboard:index")

    context = {}

    context['emails'] = NewsLetterMails.objects.all()
    return render(request, 'dashboard/newsletter/lancer_compagne_new.html', context)


# Quand il clique sur suivant présente sur lancer_compagne_new On créer une compagne et on y ajoute les emails par ajax
def lancer_compagne_add_emails(request):
    if not admin_has_permission(groupe="Newsletter", permission="Gérer les compagnes", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun email sélectionné.'})
    else:
        c = Compagne()
        c.lanceur = admin
        c.save()
        for id in ids:
            e = NewsLetterMails.objects.get(id=id)
            c.emails.add(e)

        try:
            nb_compagne = Compagne.objects.all().count() + 1
        except Exception as e:
            nb_compagne = 1

        c.titre = "Compagne #" + str(nb_compagne)
        c.save()

        return JsonResponse({'status': 'success', 'id_compagne': c.id})


# S'il lance une compagne puis revient pour modifier les emails
def lancer_compagne_emails(request, id_compagne):
    if not admin_has_permission(groupe="Newsletter", permission="Gérer les compagnes", request=request):
        return redirect("dashboard:index")

    compagne = get_object_or_404(Compagne, id=id_compagne)
    if compagne.envoyee:
        raise Http404

    context = {}

    context['emails'] = NewsLetterMails.objects.all()
    context['compagne'] = compagne
    context['compagne_emails'] = compagne.emails.all()

    return render(request, 'dashboard/newsletter/lancer_compagne_old_emails.html', context)


# Quand il clique sur suivant présente sur lancer_compagne_new On créer une compagne et on y ajoute les emails par ajax
def old_compagne_add_emails(request, id_compagne):
    if not admin_has_permission(groupe="Newsletter", permission="Gérer les compagnes", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)
    compagne = get_object_or_none(Compagne, id=id_compagne)

    if not compagne:
        return JsonResponse({'status': 'error', 'message': "Une erreur s'est produite."})

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun email sélectionné.'})
    else:
        c = compagne

        for id in ids:
            e = NewsLetterMails.objects.get(id=id)
            c.emails.add(e)

        c.save()

        return JsonResponse({'status': 'success', 'id_compagne': c.id})


# Deuxieme etape pour lancer une compagne
def lancer_compagne_contenu(request, id_compagne):
    if not admin_has_permission(groupe="Newsletter", permission="Gérer les compagnes", request=request):
        return redirect("dashboard:index")

    compagne = get_object_or_404(Compagne, id=id_compagne)
    if compagne.envoyee:
        raise Http404

    context = {}

    context['id_compagne'] = id_compagne
    context['form_compagne'] = FormAjoutCompagne(instance=compagne)

    if request.method == "POST":
        form_compagne = FormAjoutCompagne(request.POST, instance=compagne)
        if form_compagne.is_valid():
            c = form_compagne.save()
            return redirect('dashboard:lancer_compagne_confirmation', id_compagne=c.id)
        else:
            context['form_compagne'] = form_compagne
    return render(request, 'dashboard/newsletter/lancer_compagne_contenu.html', context)


# Dernière etape pour lancer une compagne : validation
def lancer_compagne_confirmation(request, id_compagne):
    if not admin_has_permission(groupe="Newsletter", permission="Gérer les compagnes", request=request):
        return redirect("dashboard:index")

    compagne = get_object_or_404(Compagne, id=id_compagne)
    if compagne.envoyee:
        raise Http404

    context = {}

    context['compagne'] = compagne

    return render(request, 'dashboard/newsletter/lancer_compagne_confirmation.html', context)


def lancer_compagne_validation(request, id_compagne):
    if not admin_has_permission(groupe="Newsletter", permission="Gérer les compagnes", request=request):
        return redirect("dashboard:index")

    compagne = get_object_or_404(Compagne, id=id_compagne)
    if compagne.envoyee:
        raise Http404

    context = {}

    context['compagne'] = compagne
    # send mails

    connection = get_custom_connection()  # Use default email connection

    # Manually open the connection
    connection.open()

    emails_list = []

    email_contenu_without_link = compagne.contenu_email

    # Original : src="media/...."
    # New : src="http://ecosysteme-btp.ma/media..."
    contenu_mail = email_contenu_without_link.replace('src="',
                                                      'src="' + request.scheme + "://" + request.META['HTTP_HOST'] + '')
    # In production we have :
    # src = "/home/ubuntu/FINALESPR/http://ecosysteme-btp.ma/media...."
    # we replace it by
    # src="http://ecosysteme-btp.ma/media..."
    contenu_mail = contenu_mail.replace(settings.MEDIA_ROOT, "")

    image_seen = "<img src=" + request.build_absolute_uri(
        reverse("dashboard:email_seen", kwargs={'id_compagne': id_compagne})) + " height=\"0\" width=\"0\">"
    contenu_mail += image_seen

    for email in compagne.emails.all().values('email'):
        email_to_send = EmailMultiAlternatives(
            compagne.titre,
            contenu_mail,
            'Ecosysteme-BTP@gmail.com',
            [email['email'], ],
        )
        email_to_send.attach_alternative(contenu_mail, "text/html")
        emails_list.append(email_to_send)

    # Send all emails in a single call -
    connection.send_messages(emails_list)
    # The connection was already open so send_messages() doesn't close it.
    # We need to manually close the connection.
    connection.close()

    compagne.envoyee = True
    compagne.save()

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Ajout"
    action.nom = "A lancé la compagne Newsletter <strong>" + compagne.titre + "</strong>"
    action.save()

    messages.success(request,
                     "La compagne a été lancée, " + str(compagne.emails.all().count()) + " emails ont été envoyés.")

    return redirect('dashboard:compagnes')


# View for seen email
def email_seen(request, id_compagne):
    compagne = get_object_or_none(Compagne, id=id_compagne)
    if compagne:
        compagne.emails_ouverts = compagne.emails_ouverts + 1
        compagne.last_seen = timezone.now()
        compagne.save()

    red = Image_PIL.new('RGB', (1, 1))
    response = HttpResponse(content_type="image/png")
    red.save(response, "PNG")
    return response


##End Newsletter


##Social Media
# General View

def socialmedia_general_view(request):
    if not admin_has_permission(groupe="Réseau social", permission="Vue d'ensemble", request=request):
        return redirect("dashboard:index")

    context = {}
    profils = Profil.objects.all()

    context['profils'] = profils
    context['derniers_inscrits'] = profils.order_by('-user__date_joined')[:10]
    context['profil_plus_vus'] = profils.order_by('-socialmedia_profil_views_number')[:10]
    context['groupes'] = Groupe.objects.all()
    context['groupes_plus_vus'] = Groupe.objects.all().order_by('-views_number')[:10]
    context['publications_plus_vus'] = Statut.objects.all().order_by('-views_number')[:10]
    context['pages_entreprises_plus_vus'] = PageEntreprise.objects.all().order_by('-views_number')[:10]
    context['offre_emploi_plus_vus'] = OffreEmploi.objects.all().order_by('-views_number')[:10]
    context['pages_entreprises'] = PageEntreprise.objects.all()
    context['offres_emploi'] = OffreEmploi.objects.all()
    context['publications'] = Statut.objects.all().reverse()
    context['influenceurs_followers_pie'] = Profil.objects.values('id', 'user__email', 'user__first_name',
                                                                  'user__last_name').annotate(
        total_follow=Count('suivi')).filter(total_follow__isnull=False).order_by('-total_follow')[:10]
    context['groupes_avec_plus_membres'] = Groupe.objects.values('id', 'nom', 'date_creation').annotate(
        total_membres=Count('adherents')).order_by('-total_membres')[:10]
    context['pages_entreprises_plus_suivis'] = PageEntreprise.objects.values('id', 'entreprise__nom').annotate(
        total_abonnes=Count('abonnees')).order_by('-total_abonnes')[:10]
    context['offres_plus_candidature'] = OffreEmploi.objects.values('id', 'nom_poste').annotate(
        total_postulants=Count('profil_postulants')).order_by('-total_postulants')[:10]

    context['statuts_plus_interactions'] = Statut.objects.filter(is_shared=False).values('id', 'contenu_statut',
                                                                                         'date_statut') \
        .annotate(total_jaime=Count('likes'), total_comments=Count('commentaire'), total_shares=F('shares_number')) \
        .annotate(total_interactions=F('total_comments') + F('total_jaime') + F('total_shares')).order_by(
        '-total_interactions')

    print(context['statuts_plus_interactions'])

    return render(request, 'dashboard/socialmedia/vue_generale.html', context)


##Groupes


def socialmedia_groups_list(request):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les groupes", request=request):
        return redirect("dashboard:index")

    context = {}

    context['groupes'] = Groupe.objects.all()

    return render(request, 'dashboard/socialmedia/lists/liste_groupes.html', context)


# Ajax
def socialmedia_delete_groups(request):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les groupes", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun groupe sélectionné.'})
    else:
        for id in ids:
            groupes_to_delete = Groupe.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé le groupe réseau social <strong>" + groupes_to_delete.nom + "</strong>"
            action.save()

            groupes_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les groupes sélectionnés ont été supprimés.'})


def socialmedia_delete_group(request, id_group):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les groupes", request=request):
        return redirect("dashboard:index")

    groupe = get_object_or_404(Groupe, id=id_group)

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Suppression"
    action.nom = "A supprimé le groupe réseau social <strong>" + groupe.nom + "</strong>"
    action.save()

    groupe.delete()

    messages.success(request,
                     "Le groupe " + groupe.nom + " a été supprimé ")

    return redirect('dashboard:socialmedia_groups_list')


def infos_group(request, id_group):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les groupes", request=request):
        return redirect("dashboard:index")

    context = {}
    groupe = get_object_or_404(Groupe, id=id_group)
    context['groupe'] = groupe
    context['publications_plus_aimes'] = list(
        groupe.statut_mur_groupe.all().values('id', 'contenu_statut').annotate(total_likes=Count('likes')).order_by(
            '-total_likes'))[:6]

    #membres_plus_statut = Statut.objects.filter(mur_groupe=groupe).annotate("profil_publicateur")
    statuts_groupe = Statut.objects.filter(mur_groupe=groupe)
    context['membres_plus_statut'] = Profil.objects.filter(publisher_statut__statut__mur_groupe=groupe).annotate(total_statut=Count("publisher_statut")).order_by('-total_statut')[:10]
    context['membres_plus_partage_statut'] = Profil.objects.raw("SELECT main_app_profil.id,  auth_user.first_name, auth_user.last_name, COUNT(*) as 'total_share' FROM SocialMedia_sharedstatut, SocialMedia_abstractstatut,SocialMedia_statut,main_app_profil,auth_user WHERE SocialMedia_sharedstatut.abstractstatut_ptr_id = SocialMedia_abstractstatut.id AND SocialMedia_statut.abstractstatut_ptr_id = SocialMedia_sharedstatut.shared_statut_id AND SocialMedia_abstractstatut.publisher_id = main_app_profil.id  AND auth_user.id = main_app_profil.user_id AND SocialMedia_statut.mur_groupe_id = %s GROUP BY  main_app_profil.id ORDER BY total_share desc LIMIT 0,10",[groupe.id])
    context['membres_plus_commentaires'] = Profil.objects.raw("Select main_app_profil.id as id,auth_user.first_name ,auth_user.last_name, Count(*) as 'total_com' from main_app_profil,SocialMedia_statut,SocialMedia_commentaire,SocialMedia_abstractstatut,auth_user  where main_app_profil.id = SocialMedia_commentaire.user_id  and SocialMedia_commentaire.statut_id = SocialMedia_abstractstatut.id and SocialMedia_abstractstatut.id = SocialMedia_statut.abstractstatut_ptr_id and SocialMedia_statut.mur_groupe_id = %s and main_app_profil.user_id = auth_user.id GROUP BY main_app_profil.id order by total_com desc limit 0,10",[groupe.id]  )



    context['derniers_commentaires'] = Commentaire.objects.filter(statut__in=groupe.statut_mur_groupe.all()).order_by(
        '-date_commentaire')

    """""""""""
    context['statuts_plus_interactions'] = Statut.objects.filter(is_shared=False) \
        .annotate(total_jaime=Count('likes'), total_comments=Count('commentaire'), total_shares=F('shares_number')) \
        .annotate(total_interactions=F('total_comments') + F('total_jaime') + F('total_shares')).order_by(
        '-total_interactions')
    """""""""""

    membres_actifs = Profil.objects.all()
    context['membres_actifs'] = membres_actifs

    # membres = groupe.adherents.all()
    # statuts_groupe = Statut.objects.filter(is_group_statut=True,id_group=groupe.id)
    # membres_stats = membres.annotate(total_likes=Count())

    return render(request, 'dashboard/socialmedia/infos/infos_group.html', context)


def socialmedia_update_groupe_profile_pic(request, id_group):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les groupes", request=request):
        return redirect("dashboard:index")

    groupe = get_object_or_404(Groupe, id=id_group)

    if request.method == "POST":

        form = FormModifierMainImage(request.POST, request.FILES)

        if form.is_valid():
            image = form.save()
            groupe.photo_profil = image
            groupe.save()
            messages.success(request, "L'image de profil du groupe a été modifiée avec succès.")
        else:
            print("no valid")
            print(form.errors)

    return redirect('dashboard:socialmedia_update_group', id_group)


def socialmedia_update_groupe_cover_pic(request, id_group):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les groupes", request=request):
        return redirect("dashboard:index")

    groupe = get_object_or_404(Groupe, id=id_group)

    if request.method == "POST":

        form = FormModifierMainImage(request.POST, request.FILES)

        if form.is_valid():
            image = form.save()
            groupe.photo_couverture = image
            groupe.save()
            messages.success(request, "L'image de couverture du groupe a été modifiée avec succès.")
        else:
            print(form.errors)

    return redirect('dashboard:socialmedia_update_group', id_group)


def socialmedia_update_group(request, id_group):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les groupes", request=request):
        return redirect("dashboard:index")

    groupe = get_object_or_404(Groupe, id=id_group)

    context = {}

    context['form'] = FormModifierGroupe(instance=groupe)
    context['groupe'] = groupe
    context['form_image_profil'] = FormModifierMainImage(instance=groupe.photo_profil)
    context['form_image_couverture'] = FormModifierMainImage(instance=groupe.photo_couverture)

    return render(request, 'dashboard/socialmedia/modification/update_group.html', context)


def socialmedia_update_group_infos(request, id_group):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les groupes", request=request):
        return redirect("dashboard:index")

    groupe = get_object_or_404(Groupe, id=id_group)

    context = {}

    if request.method == "POST":
        form = FormModifierGroupe(request.POST, instance=groupe)
        if form.is_valid():
            group = form.save()
            messages.success(request, "Le groupe a été modifié avec succès.")

    return redirect('dashboard:socialmedia_update_group', id_group)


# Profils


def socialmedia_profils_list(request):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les profils", request=request):
        return redirect("dashboard:index")

    context = {}

    context['profils'] = Profil.objects.all()

    return render(request, 'dashboard/socialmedia/lists/liste_profils.html', context)


def infos_profile(request, id_user):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les profils", request=request):
        return redirect("dashboard:index")

    context = {}

    context['profil'] = Profil.objects.get(id=id_user)
    context['statuts_aimes'] = list(Statut.objects.filter(likes__in=[context['profil']]))[:6]
    context['groupes'] = Groupe.objects.filter(admins__in=[context['profil']])
    context['pages'] = PageEntreprise.objects.filter(administrateurs__in=[context['profil']])
    context['offres'] = OffreEmploi.objects.filter(profil_publicateur=context['profil'].id)
    context['nb_amis'] = DemandeAmi.nb_amis(context['profil'])
    context['publications_partagees'] = SharedStatut.objects.filter(mur_profil=context['profil'])

    return render(request, 'dashboard/socialmedia/infos/infos_profile.html', context)


def socialmedia_update_profil(request, id_profil):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les profils", request=request):
        return redirect("dashboard:index")

    profil = get_object_or_404(Profil, id=id_profil)

    context = {}

    context['form'] = FormModifierProfil(instance=profil)
    context['form_user'] = FormModifierUserSocial(instance=profil.user)
    context['form_image_profil'] = FormModifierMainImage(instance=profil.photo_profil)
    context['form_image_couverture'] = FormModifierMainImage(instance=profil.photo_couverture)
    context['profil'] = profil

    return render(request, 'dashboard/socialmedia/modification/update_profile.html', context)


def socialmedia_update_profile_pic(request, id_user):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les profils", request=request):
        return redirect("dashboard:index")

    profil = Profil.objects.get(id=id_user)

    if request.method == "POST":

        form = FormModifierMainImage(request.POST, request.FILES)

        if form.is_valid():
            print("valid")
            image = form.save()
            profil.photo_profil = image
            profil.save()
            messages.success(request, "L'image de profil a été modifiée avec succès.")
        else:
            print("no valid")
            print(form.errors)

    return redirect('dashboard:socialmedia_update_profil', profil.id)


def socialmedia_update_cover_pic(request, id_user):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les profils", request=request):
        return redirect("dashboard:index")

    profil = Profil.objects.get(id=id_user)

    if request.method == "POST":

        form = FormModifierMainImage(request.POST, request.FILES)

        if form.is_valid():
            image = form.save()
            profil.photo_couverture = image
            profil.save()
            messages.success(request, "L'image de couverture a été modifiée avec succès.")
        else:
            print(form.errors)

    return redirect('dashboard:socialmedia_update_profil', profil.id)


def socialmedia_update_profil_infos(request, id_profil):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les profils", request=request):
        return redirect("dashboard:index")

    profil = get_object_or_404(Profil, id=id_profil)

    context = {}

    if request.method == "POST":
        form = FormModifierProfil(request.POST, instance=profil)
        form_user = FormModifierUserSocial(request.POST, instance=profil.user)
        if form.is_valid() and form_user.is_valid():
            form.save()
            form_user.save()
            messages.success(request, "Le profil a été modifié avec succès.")

    return redirect('dashboard:socialmedia_update_profil', id_profil)


# Ajax
def socialmedia_delete_profils(request):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les profils", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun profil sélectionné.'})
    else:
        for id in ids:
            profils_to_delete = Profil.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé l'utilisateur <strong>" + profils_to_delete.user.first_name + " " + profils_to_delete.user.last_name + "</strong> email : <strong>" + profils_to_delete.user.email + "</strong>"
            action.save()

            profils_to_delete.user.delete()
            profils_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les profils sélectionnés ont été supprimés.'})


def socialmedia_delete_profile(request, id_profil):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les profils", request=request):
        return redirect("dashboard:index")

    profil = get_object_or_404(Profil, id=id_profil)

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Suppression"
    action.nom = "A supprimé le profil réseau social <strong>" + profil.user.first_name.title() + " " + profil.user.last_name.title() + "</strong>"
    action.save()

    profil.user.delete()
    profil.delete()

    messages.success(request,
                     "L'utilisateur " + profil.user.first_name.title() + " " + profil.user.last_name.title() + " a été supprimé ")

    return redirect('dashboard:socialmedia_profils_list')


# Pages Entreprise


def socialmedia_page_entreprise_list(request):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les pages entreprises", request=request):
        return redirect("dashboard:index")

    context = {}

    context['pages'] = PageEntreprise.objects.all()
    return render(request, 'dashboard/socialmedia/lists/liste_pages_entreprise.html', context)


# Ajax
def socialmedia_delete_pages_entreprises(request):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les pages entreprises", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune page d\'entreprise sélectionnée.'})
    else:
        for id in ids:
            pages_to_delete = PageEntreprise.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé la page d'entreprise <strong>" + pages_to_delete.entreprise.nom + "</strong>"
            action.save()

            pages_to_delete.delete()

        return JsonResponse(
            {'status': 'success', 'message': 'Les page d\'entreprise sélectionnées ont été supprimées.'})


def socialmedia_delete_page_entreprise(request, id_page_entreprise):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les pages entreprises", request=request):
        return redirect("dashboard:index")

    page = get_object_or_404(PageEntreprise, id=id_page_entreprise)

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Suppression"
    action.nom = "A supprimé la page d'entreprise réseau social <strong>" + page.entreprise.nom + "</strong>"
    action.save()

    page.delete()

    messages.success(request,
                     "La page d'entreprise <strong>" + page.entreprise.nom + "</strong> a été supprimée ")

    return redirect('dashboard:socialmedia_page_entreprise_list')


def infos_page_entreprise(request, id_page_entreprise):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les pages entreprises", request=request):
        return redirect("dashboard:index")

    context = {}

    context['page'] = PageEntreprise.objects.get(id=id_page_entreprise)

    return render(request, 'dashboard/socialmedia/infos/infos_page_entreprise.html', context)


def socialmedia_update_page_entreprise(request, id_page_entreprise):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les pages entreprises", request=request):
        return redirect("dashboard:index")

    page = get_object_or_404(PageEntreprise, id=id_page_entreprise)

    context = {}

    form_page_entreprise = FormModifierPageEntreprise(instance=page)
    form_entreprise = FormModifierEntreprise(instance=page.entreprise)

    if request.method == "POST":
        form_page_entreprise = FormModifierPageEntreprise(request.POST, instance=page)
        form_entreprise = FormModifierEntreprise(request.POST, instance=page.entreprise)

        if form_page_entreprise.is_valid() and form_entreprise.is_valid():
            form_page_entreprise.save()
            form_entreprise.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié la page d'entreprise réseau social <strong>" + page.entreprise.nom + "</strong>"
            action.save()

            messages.success(request, "La page entreprise a été modifiée avec succès.")

    context['form_page_entreprise'] = form_page_entreprise
    context['form_entreprise'] = form_entreprise
    context['page'] = page

    return render(request, 'dashboard/socialmedia/modification/update_page_entreprise.html', context)


# Offre d'emploi


def socialmedia_offre_emploi_list(request):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les offres d'emploi", request=request):
        return redirect("dashboard:index")

    context = {}

    context['offres'] = OffreEmploi.objects.all()
    return render(request, 'dashboard/socialmedia/lists/liste_offre_emploi.html', context)


# Ajax
def socialmedia_delete_offre_emploi(request):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les offres d'emploi", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune offre d\'emploi sélectionnée.'})
    else:
        for id in ids:
            offres_to_delete = OffreEmploi.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé l'offre d'emploi <strong>" + offres_to_delete.nom_poste + "</strong> de la page d'entreprise <strong>" + offres_to_delete.page_entreprise.entreprise.nom + "</strong>"
            action.save()

            offres_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les offres d\'emploi sélectionnées ont été supprimées.'})


def socialmedia_offre_encours(request):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les offres d'emploi", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune offre d\'emploi sélectionnée.'})
    else:
        for id in ids:
            offres_to_delete = OffreEmploi.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A marqué l'offre d'emploi <strong>" + offres_to_delete.nom_poste + "</strong> de la page d'entreprise <strong>" + offres_to_delete.page_entreprise.entreprise.nom + "</strong> comme en cours"
            action.save()

            offres_to_delete.en_cours = True
            offres_to_delete.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Les offres d\'emploi sélectionnées ont été marquées comme en cours.'})


def socialmedia_offre_finie(request):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les offres d'emploi", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune offre d\'emploi sélectionnée.'})
    else:
        for id in ids:
            offres_to_delete = OffreEmploi.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A marqué l'offre d'emploi <strong>" + offres_to_delete.nom_poste + "</strong> de la page d'entreprise <strong>" + offres_to_delete.page_entreprise.entreprise.nom + "</strong> comme finie"
            action.save()

            offres_to_delete.en_cours = False
            offres_to_delete.date_fin = datetime.now()
            offres_to_delete.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Les offres d\'emploi sélectionnées ont été marquées comme finies.'})


def socialmedia_delete_offre_emploi_one(request, id_offre_emploi):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les offres d'emploi", request=request):
        return redirect("dashboard:index")

    offre = get_object_or_404(OffreEmploi, id=id_offre_emploi)

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Suppression"
    action.nom = "A supprimé l'offre d'emploi réseau social <strong>" + offre.nom_poste + "</strong> de l'entreprise <strong>" + offre.page_entreprise.entreprise.nom + "</strong>"
    action.save()

    offre.delete()

    messages.success(request,
                     "L'offre d'emploi <strong>" + offre.nom_poste + "</strong> de l'entreprise <strong>" + offre.page_entreprise.entreprise.nom + "</strong> a été supprimée")

    return redirect('dashboard:socialmedia_offre_emploi_list')


def infos_offre_emploi(request, id_offre_emploi):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les offres d'emploi", request=request):
        return redirect("dashboard:index")

    context = {}

    context['offre'] = OffreEmploi.objects.get(id=id_offre_emploi)

    context['tracking_dernieres_visites'] = Tracker.objects.filter(model_name="Offre d'emploi",
                                                                   object_id=context['offre'].id).order_by(
        '-timestamp')[:10]

    return render(request, 'dashboard/socialmedia/infos/infos_offre_emploi.html', context)


def socialmedia_update_offre_emploi(request, id_offre_emploi):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les offres d'emploi", request=request):
        return redirect("dashboard:index")

    offre = get_object_or_404(OffreEmploi, id=id_offre_emploi)

    context = {}

    form_offre = FormModifierOffreEmploi(instance=offre)

    if request.method == "POST":
        form_offre = FormModifierOffreEmploi(request.POST, instance=offre)

        if form_offre.is_valid():
            form_offre.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié l'offre d'emploi <strong>" + offre.nom_poste + "</strong> de la page entreprise <strong>" + offre.page_entreprise.entreprise.nom + " </strong>"
            action.save()

            messages.success(request, "La page entreprise a été modifiée avec succès.")

    context['form_offre'] = form_offre
    context['offre'] = offre

    return render(request, 'dashboard/socialmedia/modification/update_offre_emploi.html', context)


# Publications


def socialmedia_publications(request):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les publications", request=request):
        return redirect("dashboard:index")

    context = {}

    context['publications'] = Statut.objects.all()
    context['publications_signales'] = StatutSignales.objects.all().values("statut_signale")
    print(context['publications_signales'])

    print(context['publications'])
    return render(request, 'dashboard/socialmedia/lists/liste_publications.html', context)


# Ajax
def socialmedia_delete_publications(request):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les publications", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune publication sélectionnée.'})
    else:
        for id in ids:
            publications_to_delete = Statut.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé la publication réseau social <strong>" + publications_to_delete.contenu_statut[
                                                                              :20] + "... </strong> du profil <strong>" + publications_to_delete.publisher.user.first_name.title() + " " + publications_to_delete.publisher.user.last_name.title() + "</strong>"
            action.save()

            publications_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les publications sélectionnées ont été supprimées.'})


def socialmedia_delete_publication(request, id_publication):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les publications", request=request):
        return redirect("dashboard:index")

    publication = get_object_or_404(Statut, id=id_publication)

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Suppression"
    action.nom = "A supprimé la publication réseau social <strong>" + publication.contenu_statut[
                                                                      :20] + "... </strong> du profil <strong>" + publication.publisher.user.first_name.title() + " " + publication.publisher.user.last_name.title() + "</strong>"
    action.save()

    publication.delete()

    messages.success(request, "L'offre d'emploi <strong>" + publication.contenu_statut[
                                                            :20] + "</strong> du profil <strong>" + publication.publisher.user.first_name.title() + " " + publication.publisher.user.last_name.title() + "</strong> a été supprimée")

    return redirect('dashboard:socialmedia_publications')


def infos_publication(request, id_publication):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les publications", request=request):
        return redirect("dashboard:index")

    context = {}

    publication = get_object_or_404(Statut, id=id_publication)

    context['publication'] = publication

    return render(request, 'dashboard/socialmedia/infos/infos_publication.html', context)


def socialmedia_update_publication_all(request, id_publication):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les publications", request=request):
        return redirect("dashboard:index")

    context = {}

    context['publication'] = Statut.objects.get(id=id_publication)

    return render(request, 'dashboard/socialmedia/modification/update_publication.html', context)


def socialmedia_update_publication(request, id_publication):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les publications", request=request):
        return redirect("dashboard:index")

    pub = get_object_or_404(Statut, id=id_publication)

    if request.method == "POST":
        contenu = request.POST.get("contenu_publication", None)

        if contenu is None:
            raise Http404
        else:
            contenu = contenu.strip()  # strip = trim

        if contenu is "":
            messages.error(request, "Le contenu ne doit pas être vide.")
        else:
            pub.contenu_statut = contenu
            pub.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié le statut réseau social <strong>" + pub.contenu_statut[
                                                                        :20] + "... </strong> du profil <strong>" + pub.publisher.user.first_name.title() + " " + pub.publisher.user.last_name.title() + "</strong>"
            action.save()

            messages.success(request, "Le contenu du statut a été modifié avec succès.")

    return redirect('dashboard:socialmedia_update_publication_all', id_publication)


def socialmedia_update_publication_comment(request, id_publication, id_comment):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les publications", request=request):
        return redirect("dashboard:index")

    comment = get_object_or_404(Commentaire, id=id_comment)

    if request.method == "POST":
        contenu = request.POST.get("contenu_commentaire", None)

        if contenu is None:
            raise Http404
        else:
            contenu = contenu.strip()

        if contenu is "":
            messages.error(request, "Le contenu ne doit pas être vide.")
        else:
            comment.comment = contenu
            comment.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié le commentaire réseau social <strong>" + comment.comment[
                                                                             :20] + "... </strong> du profil <strong>" + comment.user.user.first_name.title() + " " + comment.user.user.last_name.title() + "</strong>"
            action.save()

            messages.success(request, "Le contenu du commentaire a été modifié avec succès.")

    return redirect('dashboard:socialmedia_update_publication_all', id_publication)


def socialmedia_update_publication_reply(request, id_publication, id_reply):
    if not admin_has_permission(groupe="Réseau social", permission="Gérer les publications", request=request):
        return redirect("dashboard:index")

    reply = get_object_or_404(Reply, id=id_reply)

    if request.method == "POST":
        contenu = request.POST.get("contenu_reply", None)

        if contenu is None:
            raise Http404
        else:
            contenu = contenu.strip()

        if contenu is "":
            messages.error(request, "Le contenu ne doit pas être vide.")
        else:
            reply.replyContent = contenu
            reply.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié la réponse au commentaire réseau social <strong>" + reply.replyContent[
                                                                                        :20] + "... </strong> du profil <strong>" + reply.user.user.first_name.title() + " " + reply.user.user.last_name.title() + "</strong>"
            action.save()

            messages.success(request, "Le contenu de la réponse au commentaire a été modifié avec succès.")

    return redirect('dashboard:socialmedia_update_publication_all', id_publication)


def socialmedia_activate_signal(request, id_signal):
    action = request.GET.get("action", None)

    signal = get_object_or_404(StatutSignales, id=id_signal)

    if action == "activer":
        signal.active = True
        signal.save()
    elif action == "desactiver":
        signal.active = False
        signal.save()

    response = dict()
    response['action'] = action
    response['id'] = id_signal
    response['signals_actifs'] = StatutSignales.objects.filter(active=True,
                                                               statut_signale=signal.statut_signale).count()

    return JsonResponse(response, safe=False)


## End SocialMedia


##News

# Vue Generale


def news_general_view(request):
    if not admin_has_permission(groupe="Journal", permission="Vue d'ensemble", request=request):
        return redirect("dashboard:index")

    context = {}

    news = News.objects.all()
    journalistes = Journalist.objects.all()

    context['journalistes'] = journalistes
    context['articles'] = news
    context['articles_non_approuves'] = news.filter(approved=False)
    context['nb_visites'] = news.aggregate(total_visites=Sum('view_number'))['total_visites']
    context['nb_commentaires'] = Comment.objects.all().count() + Answer.objects.all().count()
    context['nb_videos'] = Video.objects.all().count()
    context['nb_categories'] = Category.objects.all().count()
    context['journalistes_views_pie'] = journalistes.values('id', 'email', 'first_name', 'last_name').annotate(
        total_views=Sum('news__view_number')).order_by()[:10]
    context['articles_plus_vus'] = news.order_by('-view_number')[:10]

    return render(request, 'dashboard/news/vue_generale.html', context)


# Articles

def news_articles(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les produits", request=request):
        return redirect("dashboard:index")

    context = {}

    context['articles'] = News.objects.all()

    return render(request, 'dashboard/news/lists/liste_articles.html', context)


# Ajax
def delete_articles(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun article sélectionnée.'})
    else:
        for id in ids:
            article_to_delete = News.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé l'article <strong>" + str(
                article_to_delete.small_title) + "</strong> de l'auteur <strong>" + article_to_delete.journalist.first_name.title() + " " + article_to_delete.journalist.last_name.title() + "</strong> "
            action.save()

            article_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les articles sélectionnés ont été supprimés.'})


# ## JOURNALIST UPLOAD PRIMARY IMAGE ON UPDATE FUNCTION ## #
@require_POST
def news_update_primary_image(request, article_id):
    # GET TEMPORARY ARTICLE OR CREATE NEW ONE
    article = get_object_or_404(News, id=article_id)

    # GET PRIMARY IMAGE FROM POST
    form = JournalistImagePrimaryImport(request.POST, request.FILES)
    if form.is_valid():
        image = form.save()
        image.description = 'Article primary image'
        image.save()
        article.primary_image = image
        article.save()
        data = {'is_valid': True, 'name': image.image.name, 'url': image.image.url}
    else:
        data = {'is_valid': False}
    return JsonResponse(data)


# ## JOURNALIST UPLOAD SECONDARY IMAGES ON UPDATE FUNCTION ## #
@require_POST
def news_update_image(request, article_id):
    # GET TEMPORARY ARTICLE OR CREATE NEW ONE
    article = get_object_or_404(News, id=article_id)

    # GET ARTICLE IMAGES FROM POST
    form = JournalistImageImport(request.POST, request.FILES)
    if form.is_valid():
        image = form.save()
        image.article = article
        image.description = 'Article image'
        image.save()
        data = {
            'is_valid': True,
            'name': image.image.name,
            'url': image.image.url,
            'id': image.id
        }
    else:
        data = {'is_valid': False}
    return JsonResponse(data)


# ## JOURNALIST DELETE IMAGE ON UPDATE FUNCTION ## #
def news_delete_image_update(request, article_id, image_id):
    # TEST IF IMAGE AND ARTICLE BELONG TO JOURNALIST
    get_object_or_404(News, id=article_id)

    # DELETE IMAGE
    image = get_object_or_404(ImageNews, id=image_id)
    image.delete()
    data = {
        'message': 'success',
        'tr': '#tr' + str(image_id)
    }
    return JsonResponse(data)


def activer_articles(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun article sélectionnée.'})
    else:
        for id in ids:
            article_to_delete = News.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A activé l'article <strong>" + str(
                article_to_delete.small_title) + "</strong> de l'auteur <strong>" + article_to_delete.journalist.first_name.title() + " " + article_to_delete.journalist.last_name.title() + "</strong> "
            action.save()

            article_to_delete.active = True
            article_to_delete.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Les articles sélectionnés ont été marqués comme activés.'})


def desactiver_articles(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun article sélectionnée.'})
    else:
        for id in ids:
            article_to_delete = News.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A désactiver l'article <strong>" + str(
                article_to_delete.small_title) + "</strong> de l'auteur <strong>" + article_to_delete.journalist.first_name.title() + " " + article_to_delete.journalist.last_name.title() + "</strong> "
            action.save()

            article_to_delete.active = False
            article_to_delete.save()

        return JsonResponse({'status': 'success', 'message': 'Les articles sélectionnés ont été activés.'})


def verifier_articles(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun article sélectionnée.'})
    else:
        for id in ids:
            article_to_delete = News.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A approuvé l'article <strong>" + str(
                article_to_delete.small_title) + "</strong> de l'auteur <strong>" + article_to_delete.journalist.first_name.title() + " " + article_to_delete.journalist.last_name.title() + "</strong> "
            action.save()

            article_to_delete.approved = True
            article_to_delete.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Les articles sélectionnés ont été marqués comme approuvés.'})


def deverifier_articles(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun article sélectionnée.'})
    else:
        for id in ids:
            article_to_delete = News.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A marqué comme non approuvé l'article <strong>" + str(
                article_to_delete.small_title) + "</strong> de l'auteur <strong>" + article_to_delete.journalist.first_name.title() + " " + article_to_delete.journalist.last_name.title() + "</strong> "
            action.save()

            article_to_delete.approved = False
            article_to_delete.save()

        return JsonResponse({'status': 'success', 'message': 'Les articles sélectionnés ont été approuvés.'})


def signaler_articles(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun article sélectionnée.'})
    else:
        for id in ids:
            article_to_signal = News.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A marqué comme signalé l'article <strong>" + str(
                article_to_signal.small_title) + "</strong> de l'auteur <strong>" + article_to_signal.journalist.first_name.title() + " " + article_to_signal.journalist.last_name.title() + "</strong> "
            action.save()

            article_to_signal.signale = True
            article_to_signal.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Les articles sélectionnés ont été marqués comme signalés.'})


def designaler_articles(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun article sélectionnée.'})
    else:
        for id in ids:
            article_to_delete = News.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A marqué comme non signalé l'article <strong>" + str(
                article_to_delete.small_title) + "</strong> de l'auteur <strong>" + article_to_delete.journalist.first_name.title() + " " + article_to_delete.journalist.last_name.title() + "</strong> "
            action.save()

            article_to_delete.signale = False
            article_to_delete.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Les articles sélectionnés ont été marqué comme non signalés.'})


def delete_article(request, id_article):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    article = get_object_or_404(News, id=id_article)

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Suppression"
    action.nom = "A supprimé l'article du journal <strong>" + article.small_title + "</strong> du journaliste <strong>" + article.journalist.first_name.title() + " " + article.journalist.last_name.title() + "</strong>"
    action.save()

    article.delete()

    messages.success(request,
                     "L'article <strong>" + article.small_title + "</strong> a été supprimé ")

    return redirect('dashboard:news_articles')


def news_infos_article(request, id_article):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    context = {}

    article = get_object_or_404(News, id=id_article)

    context['article'] = article

    context['nb_signals'] = SignalComment.objects.filter(
        comment__in=article.comment_set.all().values('id')).count() + SignalAnswer.objects.filter(
        answer__comment__in=article.comment_set.all().values('id')).count()

    context['tracking_dernieres_visites'] = Tracker.objects.filter(model_name="Article", object_id=article.id).order_by(
        '-timestamp')[:10]

    return render(request, 'dashboard/news/infos/infos_article.html', context)


def update_article(request, id_article):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    article = get_object_or_404(News, id=id_article)

    context = {}

    form_article = FormModifierArticle(instance=article)

    if request.method == "POST":
        form_article = FormModifierArticle(request.POST, instance=article)

        if form_article.is_valid():
            form_article.save()
            messages.success(request, "L'article a été modifié avec succès")

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié l'article du journal <strong>" + article.small_title + "</strong> du journaliste <strong>" + article.journalist.first_name.title() + " " + article.journalist.last_name.title() + "</strong>"
            action.save()

    context['article'] = article
    context['form_article'] = form_article

    return render(request, 'dashboard/news/modifications/update_article.html', context)


# Articles videos

def news_articles_videos(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles vidéos", request=request):
        return redirect("dashboard:index")

    context = {}

    context['articles_videos'] = Video.objects.all()

    return render(request, 'dashboard/news/lists/liste_articles_videos.html', context)


# Ajax
def delete_articles_videos(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles vidéos", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun article vidéo sélectionnée.'})
    else:
        for id in ids:
            article_video_to_delete = Video.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé la l'article vidéo <strong>" + str(
                article_video_to_delete.small_title) + "</strong> de l'auteur <strong>" + article_video_to_delete.journalist.first_name.title() + " " + article_video_to_delete.journalist.last_name.title() + "</strong> "
            action.save()

            article_video_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les articles vidéos sélectionnés ont été supprimés.'})


def activer_articles_videos(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun article vidéo sélectionnée.'})
    else:
        for id in ids:
            article_to_delete = Video.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A activé l'article vidéo <strong>" + str(
                article_to_delete.small_title) + "</strong> de l'auteur <strong>" + article_to_delete.journalist.first_name.title() + " " + article_to_delete.journalist.last_name.title() + "</strong> "
            action.save()

            article_to_delete.active = True
            article_to_delete.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Les articles sélectionnés ont été marqués comme activés.'})


def desactiver_articles_videos(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun article vidéo sélectionnée.'})
    else:
        for id in ids:
            article_to_delete = Video.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A désactiver l'article vidéo <strong>" + str(
                article_to_delete.small_title) + "</strong> de l'auteur <strong>" + article_to_delete.journalist.first_name.title() + " " + article_to_delete.journalist.last_name.title() + "</strong> "
            action.save()

            article_to_delete.active = False
            article_to_delete.save()

        return JsonResponse({'status': 'success', 'message': 'Les articles vidéo sélectionnés ont été activés.'})


def verifier_articles_videos(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun article vidéo sélectionnée.'})
    else:
        for id in ids:
            article_to_delete = Video.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A approuvé l'article vidéo <strong>" + str(
                article_to_delete.small_title) + "</strong> de l'auteur <strong>" + article_to_delete.journalist.first_name.title() + " " + article_to_delete.journalist.last_name.title() + "</strong> "
            action.save()

            article_to_delete.approved = True
            article_to_delete.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Les articles vidéo sélectionnés ont été marqués comme approuvés.'})


def deverifier_articles_videos(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun article vidéo sélectionnée.'})
    else:
        for id in ids:
            article_to_delete = Video.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A marqué comme non approuvé l'article vidéo <strong>" + str(
                article_to_delete.small_title) + "</strong> de l'auteur <strong>" + article_to_delete.journalist.first_name.title() + " " + article_to_delete.journalist.last_name.title() + "</strong> "
            action.save()

            article_to_delete.approved = False
            article_to_delete.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Les articles vidéo sélectionnés ont été marqué comme non approuvés.'})


def news_infos_article_videos(request, id_article_videos):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles vidéos", request=request):
        return redirect("dashboard:index")

    context = {}

    article = get_object_or_404(Video, id=id_article_videos)

    context['article'] = article

    context['nb_signals'] = SignalComment.objects.filter(
        comment__in=article.comment_set.all().values('id')).count() + SignalAnswer.objects.filter(
        answer__comment__in=article.comment_set.all().values('id')).count()

    context['tracking_dernieres_visites'] = Tracker.objects.filter(model_name="Article Vidéo",
                                                                   object_id=article.id).order_by('-timestamp')[:10]

    return render(request, 'dashboard/news/infos/infos_article_videos.html', context)


def delete_article_video(request, id_article_video):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    article = get_object_or_404(Video, id=id_article_video)

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Suppression"
    action.nom = "A supprimé l'article vidéo du journal <strong>" + article.small_title + "</strong> du journaliste <strong>" + article.journalist.first_name.title() + " " + article.journalist.last_name.title() + "</strong>"
    action.save()

    article.delete()

    messages.success(request,
                     "L'article vidéo <strong>" + article.small_title + "</strong> a été supprimé ")

    return redirect('dashboard:news_articles_videos')


def update_article_video(request, id_article):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    article = get_object_or_404(Video, id=id_article)

    context = {}

    form_article = FormModifierArticleVideo(instance=article)

    if request.method == "POST":
        form_article = FormModifierArticleVideo(request.POST, instance=article)

        if form_article.is_valid():
            form_article.save()
            messages.success(request, "L'article a été modifié avec succès")

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié l'article vidéo du journal <strong>" + article.small_title + "</strong> du journaliste <strong>" + article.journalist.first_name.title() + " " + article.journalist.last_name.title() + "</strong>"
            action.save()

    context['article'] = article
    context['form_article'] = form_article

    return render(request, 'dashboard/news/modifications/update_article_video.html', context)


# Journalistes

def news_journalistes(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les journalistes", request=request):
        return redirect("dashboard:index")

    context = {}

    context['journalistes'] = Journalist.objects.annotate(views=Sum('news__view_number'))

    return render(request, 'dashboard/news/lists/liste_journalistes.html', context)


# Ajax
def delete_journalistes(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les journalistes", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun journaliste sélectionné.'})
    else:
        for id in ids:
            journaliste_to_delete = Journalist.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé le journaliste <strong>" + journaliste_to_delete.first_name + " " + journaliste_to_delete.last_name + "</strong>"
            action.save()

            journaliste_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les journalistes sélectionnés ont été supprimés.'})


def delete_journaliste(request, id_journaliste):
    if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    journaliste = get_object_or_404(Journalist, id=id_journaliste)

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Suppression"
    action.nom = "A supprimé le journaliste <strong>" + journaliste.first_name + " " + journaliste.last_name + "</strong>"
    action.save()

    user = get_object_or_none(User, email=journaliste.email)
    if user is not None:
        user.profile.delete()
        user.delete()

    journaliste.delete()

    messages.success(request,
                     "Le journaliste <strong>" + journaliste.first_name + " " + journaliste.last_name + "</strong> a été supprimé ")

    return redirect('dashboard:news_journalistes')


def news_infos_journaliste(request, id_journaliste):
    if not admin_has_permission(groupe="Journal", permission="Gérer les journalistes", request=request):
        return redirect("dashboard:index")

    context = {}

    journaliste = Journalist.objects.get(id=id_journaliste)

    context['journaliste'] = journaliste
    context['derniers_articles'] = News.objects.filter(journalist=journaliste).order_by('-date_publication')[
                                   :6]
    context['derniers_vues'] = News.objects.filter(journalist=journaliste).order_by('-view_number')[:6]
    context['visites_total'] = News.objects.filter(journalist=journaliste).aggregate(Sum('view_number'))[
        'view_number__sum']

    context['visites_total'] = Tracker.objects.filter(model_name="Journaliste", object_id=journaliste.id).count()
    context['tracking_dernieres_visites'] = Tracker.objects.filter(model_name="Journaliste",
                                                                   object_id=journaliste.id).order_by('-timestamp')[:10]
    return render(request, 'dashboard/news/infos/infos_journaliste.html', context)


def update_journaliste(request, id_journaliste):
    if not admin_has_permission(groupe="Journal", permission="Gérer les journalistes", request=request):
        return redirect("dashboard:index")

    journaliste = get_object_or_404(Journalist, id=id_journaliste)

    context = {}

    form_journaliste = FormModifierJournaliste(instance=journaliste)

    if request.method == "POST":
        form_journaliste = FormModifierJournaliste(request.POST, instance=journaliste)

        if form_journaliste.is_valid():
            form_journaliste.save()
            messages.success(request, "Le journaliste a été modifié avec succès.")

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié le journaliste <strong>" + journaliste.first_name + " " + journaliste.last_name + "</strong>"
            action.save()

    context['journaliste'] = journaliste
    context['form_journaliste'] = form_journaliste

    return render(request, 'dashboard/news/modifications/update_journaliste.html', context)


# Signalements

def news_signalements(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les journalistes", request=request):
        return redirect("dashboard:index")

    context = {}

    context['signalements'] = SignalComment.objects.all()

    return render(request, 'dashboard/news/lists/signalements.html', context)


# Ajax
def delete_signalements(request):
    if not admin_has_permission(groupe="Journal", permission="Gérer les signalements", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun signalement sélectionné.'})
    else:
        for id in ids:
            signal_comment_to_delete = SignalComment.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé le signalement <strong>" + signal_comment_to_delete.cause + "</strong> sur l'article </strong>" + signal_comment_to_delete.comment.news.small_title + "</strong>"
            action.save()

            signal_comment_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les signalements sélectionnés ont été supprimés.'})


# Reseaux sociaux et bannieres

def news_reseaux_bannieres(request):
    return render(request, 'dashboard/news/reseaux_bannieres.html')


# News commmentaires
# News Answers

def news_delete_comment(request, id_comment, article_type):
    if article_type == "video":
        if not admin_has_permission(groupe="Journal", permission="Gérer les articles vidéos", request=request):
            return redirect("dashboard:index")
    elif article_type == "normal":
        if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
            return redirect("dashboard:index")
    else:
        raise Http404

    comment = get_object_or_404(Comment, id=id_comment)

    messages.success(request, "Le commentaire a été supprimé avec succès.")

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Modification"
    action.nom = "A supprimé le commentaire <strong>" + comment.message[
                                                        :20] + "</strong> de l'article du Journal <strong>" + comment.news.small_title + "</strong>"
    action.save()

    comment.delete()

    if article_type is "video":
        return redirect('dashboard:news_infos_article_videos', comment.news.id)

    return redirect('dashboard:news_infos_article', comment.news.id)


def news_delete_answer(request, id_answer, article_type):
    if article_type == "video":
        if not admin_has_permission(groupe="Journal", permission="Gérer les articles vidéos", request=request):
            return redirect("dashboard:index")
    elif article_type == "normal":
        if not admin_has_permission(groupe="Journal", permission="Gérer les articles", request=request):
            return redirect("dashboard:index")
    else:
        raise Http404

    answer = get_object_or_404(Answer, id=id_answer)

    messages.success(request, "La réponse au commentaire a été supprimée avec succès.")

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Modification"
    action.nom = "A supprimé la réponse <strong>" + answer.message[
                                                    :20] + "</strong> sur l'article du Journal <strong>" + answer.comment.news.small_title + "</strong>"
    action.save()

    answer.delete()

    if article_type is "video":
        return redirect('dashboard:news_infos_article_videos', answer.comment.news.id)

    return redirect('dashboard:news_infos_article', answer.comment.news.id)


##End News


##Market Place

# Vue Generale


def marketplace_general_view(request):
    context = {}
    """""""""""
    # Google Analytics : Unique Views for All ecommerce module
    m = Metrics().add_metric_expression(metric="ga:uniquePageViews")
    d = Dimensions().add_dimension_name("ga:pagePathLevel1")
    f = Filters().add_filter("ga:pagePathLevel1","EXACT",["/e_commerce/"])


    # Google Analytics : All Views for All ecommerce module
    m2 = Metrics().add_metric_expression(metric="ga:pageViews")
    d2 = Dimensions().add_dimension_name("ga:pagePathLevel1")

    f2 = Filters().add_filter("ga:pagePathLevel1", "EXACT", ["/e_commerce/"])

    context['unique_views_all_ecommerce'] = get_scalar_result_analytics(start_date="2018-08-30",end_date="2018-09-05",metrics=m,dimensions=d,filters=f)
    context['all_views_all_ecommerce'] = get_scalar_result_analytics(start_date="2018-08-30", end_date="2018-09-05", metrics=m2,
                                                             dimensions=d2, filters=f2)
    """""""""""

    # Ventes ces 12 derniers mois
    last_seven_months = datetime.today() - timedelta(days=365)  # last 365 days
    ventes = OrderLine.objects.filter(order__date__gt=last_seven_months).annotate(
        month=ExtractMonth('order__date')).values('month').annotate(total_ventes=Sum('total')).order_by()

    context['nb_boutiques'] = Shop.objects.filter(approved=True).count()
    context['nb_produits'] = Product.objects.filter(approved=True).count()
    context['prix_ventes'] = Order.objects.all().aggregate(total_ventes=Sum('amount'))['total_ventes']
    context['commandes'] = Order.objects.all()
    context['demandes_devis'] = MessageSupplier.objects.count()
    context['ventes'] = ventes
    context['produits'] = Product.objects.filter(approved=False).reverse()[:7]
    context['exposants_requests'] = Shop.objects.filter(approved=False).reverse()[:7]
    context['cart'] = Cart.objects.all().count()
    context['wish'] = WishList.objects.all().count()
    context['produits_plus_visites'] = Product.objects.all().order_by('-number_views')[:10]
    context['boutiques_plus_visites'] = Shop.objects.all().order_by('-number_visitors')[:10]
    context['produits_plus_recherches'] = Product.objects.all().annotate(total_search=Count('resultsearch')).order_by(
        '-total_search')[:10]

    print(context['produits_plus_recherches'])

    return render(request, 'dashboard/marketplace/vue_generale.html', context)


# Commandes

def marketplace_orders(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les commandes", request=request):
        return redirect("dashboard:index")

    context = {}
    context['commandes'] = Order.objects.all()

    return render(request, 'dashboard/marketplace/lists/orders.html', context)


def delete_orders(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les commandes", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune commande sélectionnée.'})
    else:
        for id in ids:
            order_to_delete = Order.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé la commande <strong>" + str(
                order_to_delete.id) + "</strong> de l'utilisateur <strong>" + order_to_delete.user.user.first_name.title() + " " + order_to_delete.user.user.last_name.title() + "</strong> "
            action.save()

            order_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les commandes sélectionnées ont été supprimées.'})


def change_commande_status(request, status_name):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les commandes", request=request):
        return redirect("dashboard:index")

    if status_name != "Created" and status_name != "Processing" and status_name != "Shipped":
        return JsonResponse({'status': 'error', 'message': 'Une erreur fatale s\'est produite.'})

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune commande sélectionnée.'})
    else:
        for id in ids:
            commande = Order.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A marqué le statut de la commande   <strong> #" + str(
                commande.id) + " </strong> comme <strong>" + status_name + "</strong> "
            action.save()

            commande.status = status_name
            commande.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Les commandes sélectionnées ont été marqué comme ' + status_name + '.'})


def marketplace_order(request, id_order):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les commandes", request=request):
        return redirect("dashboard:index")

    order = get_object_or_404(Order, id=id_order)

    context = {}

    context['order'] = order

    return render(request, 'dashboard/marketplace/infos/order.html', context)


# Produits

def marketplace_products(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les produits", request=request):
        return redirect("dashboard:index")

    context = {}

    context['produits'] = Product.objects.annotate(nb_ventes=Sum('orderline__quantity'))

    return render(request, 'dashboard/marketplace/lists/produits.html', context)


def marketplace_products_to_approve(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les produits", request=request):
        return redirect("dashboard:index")

    context = {}

    context['produits'] = Product.objects.filter(approved=False)

    return render(request, 'dashboard/marketplace/lists/produits_approuver.html', context)


# Ajax
def delete_products(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les produits", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun produit sélectionné.'})
    else:
        for id in ids:
            product_to_delete = Product.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé le produit <strong>" + product_to_delete.name + "</strong> de la boutique <strong>" + product_to_delete.supplier.name + "</strong> "
            action.save()

            product_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les produits sélectionnés ont été supprimés.'})


@require_POST
def up_product_upload_image(request, product_id):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les produits", request=request):
        return redirect("dashboard:index")

    product = get_object_or_404(Product, id=product_id)

    # GET Product IMAGES FROM POST
    form = ProductImageImport(request.POST, request.FILES)
    if form.is_valid():
        image = form.save()
        image.product = product
        image.save()
        data = {
            'is_valid': True,
            'name': image.image.name,
            'url': image.image.url,
            'id': image.id
        }
    else:
        data = {'is_valid': False}
    return JsonResponse(data)


def up_product_delete_image(request, image_id):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les produits", request=request):
        return redirect("dashboard:index")

    image = get_object_or_404(CommerceImage, id=image_id)

    image.delete()

    data = {
        'message': 'success',
        'tr': '#tr' + str(image_id)
    }
    return JsonResponse(data)

    return redirect('e_commerce:index')


def approve_products(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les produits", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun produit sélectionné.'})
    else:
        for id in ids:
            product_to_delete = Product.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A approuvé le produit <strong>" + product_to_delete.name + "</strong> de la boutique <strong>" + product_to_delete.supplier.name + "</strong> "
            action.save()

            product_to_delete.approved = True
            product_to_delete.save()

        return JsonResponse({'status': 'success', 'message': 'Les produits sélectionnés ont été approuvés.'})


def desapprove_products(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les produits", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun produit sélectionné.'})
    else:
        for id in ids:
            product_to_delete = Product.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A marqué comme non approuvé le produit <strong>" + product_to_delete.name + "</strong> de la boutique <strong>" + product_to_delete.supplier.name + "</strong> "
            action.save()

            product_to_delete.approved = False
            product_to_delete.save()

        return JsonResponse(
            {'status': 'success', 'message': 'Les produits sélectionnés ont été marqués comme non approuvés.'})


def non_vente_products(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les produits", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun produit sélectionné.'})
    else:
        for id in ids:
            product_to_delete = Product.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A retiré de la  vente le produit <strong>" + product_to_delete.name + "</strong> de la boutique <strong>" + product_to_delete.supplier.name + "</strong> "
            action.save()

            product_to_delete.active = False
            product_to_delete.save()

        return JsonResponse({'status': 'success', 'message': 'Les produits sélectionnés ont été retirés de la vente.'})


def vente_products(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les produits", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun produit sélectionné.'})
    else:
        for id in ids:
            product_to_delete = Product.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A mis en vente le produit <strong>" + product_to_delete.name + "</strong> de la boutique <strong>" + product_to_delete.supplier.name + "</strong> "
            action.save()

            product_to_delete.active = True
            product_to_delete.save()

        return JsonResponse({'status': 'success', 'message': 'Les produits sélectionnés ont été mis en vente.'})


def marketplace_product(request, id_product):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les produits", request=request):
        return redirect("dashboard:index")

    produit = get_object_or_404(Product, id=id_product)

    context = {}

    nb_vendu = 0
    disponible = 0

    for order_line in OrderLine.objects.filter(product=produit):
        nb_vendu += order_line.quantity

    for stock in Stock.objects.filter(product=produit):
        disponible += stock.quantity

    context['produit'] = produit
    context['vendu_nb'] = nb_vendu
    context['stock_nb'] = disponible

    context['tracking_dernieres_visites'] = Tracker.objects.filter(model_name="Produit", object_id=produit.id).order_by(
        '-timestamp')[:10]

    return render(request, 'dashboard/marketplace/infos/produit.html', context)


def delete_product(request, id_product):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les produits", request=request):
        return redirect("dashboard:index")

    produit = get_object_or_404(Product, id=id_product)

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Suppression"
    action.nom = "A supprimé le produit <strong> #" + str(produit.id) + " " + produit.name + "</strong>"
    action.save()

    messages.success(request,
                     "Le produit <strong> #" + str(produit.id) + " " + produit.name + "</strong> a été supprimé ")

    produit.delete()

    return redirect('dashboard:marketplace_products')


def update_product(request, id_product):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les produits", request=request):
        return redirect("dashboard:index")

    produit = get_object_or_404(Product, id=id_product)

    context = {}

    form_produit = FormModifierProduit(instance=produit)

    if request.method == "POST":
        form_produit = FormModifierProduit(request.POST, instance=produit)

        if form_produit.is_valid():
            form_produit.save()
            messages.success(request, "Le produit a été modifié avec succès.")

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié le produit <strong> #" + str(produit.id) + " " + produit.name + "</strong>"
            action.save()
        else:
            print(form_produit.errors)

    context['produit'] = produit
    context['form_produit'] = form_produit
    context['images'] = produit.commerceimage_set.all()

    return render(request, 'dashboard/marketplace/modification/update_produit.html', context)


# Boutiques

def marketplace_shops(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les boutiques", request=request):
        return redirect("dashboard:index")

    shops_brut = Shop.objects.filter(approved=True)
    context = {}
    shops = {}

    context['boutiques'] = []

    for shop in shops_brut:
        boutique = Boutique()  # Boutique = Dynamic Class
        products = shop.product_set.all()

        boutique.id = shop.id
        boutique.nom = shop.name
        boutique.vues = shop.number_visitors
        boutique.date_creation = shop.date_creation
        try:
            boutique.exposant = shop.owner
        except:
            boutique.exposant = None
        boutique.produits = shop.product_set.all().count()
        boutique.total = OrderLine.objects.filter(product__in=products).aggregate(Sum('total'))['total__sum']

        context['boutiques'].append(boutique)

    return render(request, 'dashboard/marketplace/lists/shops.html', context)


def marketplace_shop(request, id_shop):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les boutiques", request=request):
        return redirect("dashboard:index")

    boutique = get_object_or_404(Shop, id=id_shop)

    context = {}

    produits = boutique.product_set.all()
    total = OrderLine.objects.filter(product__in=produits).aggregate(Sum('total'))['total__sum']

    last_seven_months = datetime.today() - timedelta(days=220)  # last 220 days = 7 months
    ventes = OrderLine.objects.filter(product__in=produits, order__date__gt=last_seven_months).annotate(
        month=ExtractMonth('order__date')).values('month').annotate(total_ventes=Sum('total')).order_by()

    ventes_total_produits = []

    for produit in produits:
        tot = OrderLine.objects.filter(product=produit).aggregate(produit_total=Sum('total'))['produit_total']
        if tot:
            vente_one_product = {}
            vente_one_product['nom_produit'] = produit.name
            vente_one_product['total'] = tot

            ventes_total_produits.append(vente_one_product)

    ventes_total_produits.sort(key=operator.itemgetter('total'), reverse=True)

    context['boutique'] = boutique
    context['total'] = total
    context['ventes'] = ventes
    context['ventes_pie'] = ventes_total_produits[:6]
    context['produits_plus_vus'] = Product.objects.filter(supplier_id=id_shop).order_by('-number_views')[:12]

    context['tracking_dernieres_visites'] = Tracker.objects.filter(model_name="Boutique",
                                                                   object_id=boutique.id).order_by('-timestamp')[:10]

    return render(request, 'dashboard/marketplace/infos/shop.html', context)


def delete_shops(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les boutiques", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune boutique sélectionnée.'})
    else:
        for id in ids:
            shop_to_delete = Shop.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé la boutique <strong>" + shop_to_delete.name.title() + "</strong> de l'utilisateur <strong>" + shop_to_delete.owner.user.first_name.title() + " " + shop_to_delete.owner.user.last_name.title() + "</strong> "
            action.save()

            shop_to_delete.delete()

        return JsonResponse({'status': 'success', 'message': 'Les boutiques sélectionnées ont été supprimées.'})


def approve_shops(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les boutiques", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune boutique sélectionnée.'})
    else:
        for id in ids:
            shop_to_delete = Shop.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A approuvé la boutique <strong>" + shop_to_delete.name.title() + "</strong> de l'utilisateur <strong>" + shop_to_delete.owner.user.first_name.title() + " " + shop_to_delete.owner.user.last_name.title() + "</strong> "
            action.save()

            shop_to_delete.approved = True
            shop_to_delete.save()

        return JsonResponse({'status': 'success', 'message': 'Les boutiques sélectionnées ont été approuvées.'})


def delete_shop(request, id_shop):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les boutiques", request=request):
        return redirect("dashboard:index")

    boutique = get_object_or_404(Shop, id=id_shop)

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Suppression"
    action.nom = "A supprimé la boutique <strong> " + boutique.name + "</strong> de l'utilisateur <strong>" + boutique.owner.user.first_name.title() + " " + boutique.owner.user.last_name.title() + "</strong>"
    action.save()

    messages.success(request,
                     "La la boutique <strong> " + boutique.name + "</strong> de l'utilisateur <strong>" + boutique.owner.user.first_name.title() + " " + boutique.owner.user.last_name.title() + "</strong> a été supprimée")

    boutique.delete()

    return redirect('dashboard:marketplace_shops')


def update_shop(request, id_shop):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les boutiques", request=request):
        return redirect("dashboard:index")

    boutique = get_object_or_404(Shop, id=id_shop)

    context = {}

    form_boutique = FormModifierBoutique(instance=boutique)

    if request.method == "POST":
        form_boutique = FormModifierBoutique(request.POST, instance=boutique)

        if form_boutique.is_valid():
            form_boutique.save()
            messages.success(request, "La boutique a été modifié avec succès.")

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié la boutique <strong> " + boutique.name + "</strong>"
            action.save()
        else:
            print(form_boutique.errors)

    context['boutique'] = boutique
    context['form_boutique'] = form_boutique

    return render(request, 'dashboard/marketplace/modification/update_shop.html', context)


# Reseaux sociaux + bannieres

def marketplace_reseaux_bannieres(request):
    return render(request, 'dashboard/marketplace/reseaux_bannieres.html')


# Reseaux sociaux + bannieres

def marketplace_exposants_requests(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les boutiques", request=request):
        return redirect("dashboard:index")

    context = {}

    context['exposants'] = Shop.objects.filter(approved=False)

    return render(request, 'dashboard/marketplace/lists/exposants_demande.html', context)


# Catégories

# ....

# Sous Catégories

def marketplace_add_category_level_one(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les catégories", request=request):
        return redirect("dashboard:index")

    context = {}

    form = FormEcommerceCategory(request.POST or None,request.FILES or None)

    if request.method == "POST":
        if form.is_valid():
            cat = form.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Ajout"
            action.nom = "A ajouté la catégorie Ecommerce de <strong>" + cat.name + "</strong> "
            action.save()

        messages.success(request, "La catégorie a été ajoutée.")
        return redirect('dashboard:marketplace_manage_categories')

    context['form'] = form

    return render(request, 'dashboard/marketplace/add_category_niveau_I.html', context)


def marketplace_manage_categories(request):
    if not admin_has_permission(groupe="Ecommerce", permission="Gérer les catégories", request=request):
        return redirect("dashboard:index")

    context = {}
    # --------------- All Categories ---------------
    context['categories'] = CommerceCategory.objects.all().order_by("-pk")

    # ------------- Variables venant de redirection ------------------
    category_id = request.session.get('category_id', None)
    category_level = request.session.get('category_level', None)

    # On va utiliser ces deux variables pour scroll jusqu'au dernieres categories ajoutées/modifiées
    if category_level is not None and category_id is not None:
        context['category_id'] = category_id
        context['category_level'] = category_level
        del request.session['category_id']
        del request.session['category_level']

    return render(request, 'dashboard/marketplace/gestion_categories.html', context)


def marketplace_add_category(request, category_level, category_parent_id):
    category_name = request.GET.get("category_name", None)
    if category_name is None:
        raise Http404()

    if category_level in [2, 3, 4]:

        request.session['category_level'] = category_level

        if category_level == 2:
            c_parent = CommerceCategory(id=category_parent_id)

            c = CommerceSCategoryOne()
            c.name = category_name
            c.category = c_parent
            c.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Ajout"
            action.nom = "A ajouté la catégorie de niveau II <strong>" + c.name + "</strong> (Ecommerce) "
            action.save()

            request.session['category_id'] = c.id

        if category_level == 3:
            c_parent = CommerceSCategoryOne(id=category_parent_id)
            c = CommerceSCategoryTwo()
            c.name = category_name
            c.category_one = c_parent
            c.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Ajout"
            action.nom = "A ajouté la catégorie de niveau III <strong>" + c.name + "</strong> (Ecommerce) "
            action.save()

            request.session['category_id'] = c.id

        if category_level == 4:
            c_parent = CommerceSCategoryTwo(id=category_parent_id)
            c = CommerceSCategory()
            c.name = category_name
            c.category_two = c_parent
            c.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Ajout"
            action.nom = "A ajouté la catégorie de niveau IV <strong>" + c.name + "</strong> (Ecommerce) "
            action.save()

            request.session['category_id'] = c.id

    return redirect('dashboard:marketplace_manage_categories')


def marketplace_update_category(request, category_level, category_id):
    category_name = request.GET.get("category_name", None)
    if category_name is None:
        raise Http404()

    if category_level in [1, 2, 3, 4]:

        request.session['category_level'] = category_level
        request.session['category_id'] = category_id

        if category_level == 1:
            c = CommerceCategory.objects.get(id=category_id)
            c.name = category_name
            c.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié la catégorie de niveau I <strong>" + c.name + "</strong> (Ecommerce) "
            action.save()

        if category_level == 2:
            c = CommerceSCategoryOne.objects.get(id=category_id)
            c.name = category_name
            c.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié la catégorie de niveau II <strong>" + c.name + "</strong> (Ecommerce) "
            action.save()

        if category_level == 3:
            c = CommerceSCategoryTwo.objects.get(id=category_id)
            c.name = category_name
            c.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié la catégorie de niveau III <strong>" + c.name + "</strong> (Ecommerce) "
            action.save()

        if category_level == 4:
            c = CommerceSCategory.objects.get(id=category_id)
            c.name = category_name
            c.save()

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié la catégorie de niveau IV <strong>" + c.name + "</strong> (Ecommerce) "
            action.save()

    return redirect('dashboard:marketplace_manage_categories')


def marketplace_delete_category(request, category_level, category_id):
    if category_level in [1, 2, 3, 4]:

        request.session['category_level'] = category_level
        request.session['category_id'] = category_id

        context_success = {'status': 'success', 'message': "La catégorie a été supprimée"}

        if category_level == 1:
            c = CommerceCategory.objects.get(id=category_id)

            c2_set = c.commercescategoryone_set.all()
            message = "Les produits avec les codes : \n"

            count_products_1 = 0

            for c2 in c2_set:
                for c3_set in c2.commercescategorytwo_set.all():
                    for c4_set in c3_set.commercescategory_set.all():
                        for product in c4_set.product_set.all():
                            message += "#" + str(product.id) + " "
                            count_products_1 += 1

            message += "\nvont être supprimés aussi!\nVeuillez changer leur catégorie avant de supprimer cette dernière!"

            if count_products_1 == 0:

                action = Action()
                action.date = timezone.now()
                action.admin = admin_logged(request)
                action.type = "Suppression"
                action.nom = "A supprimé la catégorie de niveau I <strong>" + c.name + "</strong> (Ecommerce) "
                action.save()

                context = context_success
            else:
                context = {'status': 'warning', 'message': message}

        if category_level == 2:
            c = CommerceSCategoryOne.objects.get(id=category_id)

            c3_set = c.commercescategorytwo_set.all()
            message = "Les produits avec les codes : \n"

            count_products_2 = 0

            for c4_set in c3_set:
                for category4 in c4_set.commercescategory_set.all():
                    for product in category4.product_set.all():
                        message += "#" + str(product.id) + " "
                        count_products_2 += 1

            message += "\nvont être supprimés aussi!\nVeuillez changer leur catégorie avant de supprimer cette dernière!"

            if count_products_2 == 0:
                action = Action()
                action.date = timezone.now()
                action.admin = admin_logged(request)
                action.type = "Suppression"
                action.nom = "A supprimé la catégorie de niveau II <strong>" + c.name + "</strong> (Ecommerce) "
                action.save()

                c.delete()
                context = context_success
            else:
                context = {'status': 'warning', 'message': message}

        if category_level == 3:
            c = CommerceSCategoryTwo.objects.get(id=category_id)
            c4_set = c.commercescategory_set.all()
            message = "Les produits avec les codes : \n"

            count_products_3 = 0

            for category4 in c4_set:
                for product in category4.product_set.all():
                    message += "#" + str(product.id) + " "
                    count_products_3 += 1

            message += "\nvont être supprimés aussi!\nVeuillez changer leur catégorie avant de supprimer cette dernière!"

            if count_products_3 == 0:

                action = Action()
                action.date = timezone.now()
                action.admin = admin_logged(request)
                action.type = "Suppression"
                action.nom = "A supprimé la catégorie de niveau III <strong>" + c.name + "</strong> (Ecommerce) "
                action.save()

                c.delete()

                context = context_success
            else:
                context = {'status': 'warning', 'message': message}

        if category_level == 4:
            c = CommerceSCategory.objects.get(id=category_id)
            count_products_4 = c.product_set.all().count()

            if (count_products_4 == 0):
                action = Action()
                action.date = timezone.now()
                action.admin = admin_logged(request)
                action.type = "Suppression"
                action.nom = "A supprimé la catégorie de niveau IV <strong>" + c.name + "</strong> (Ecommerce) "
                action.save()

                c.delete()
                context = context_success
            else:
                message = "Les produits avec les codes : \n"

                for product in c.product_set.all():
                    message += "#" + str(product.id) + " "

                message += "\nvont être supprimés aussi!\nVeuillez changer leur catégorie avant de supprimer cette dernière!"
                context = {'status': 'warning', 'message': message}


    else:
        context = {'status': 'error', 'message': "Une erreur s'est produite!"}

    return JsonResponse(context)


##End Market Place #~


########### BEGIN Q and A ###########
# QA

def qa_general_view(request):
    if not admin_has_permission(groupe="QA", permission="Vue d'ensemble", request=request):
        return redirect("dashboard:index")

    context = {}
    context['questions'] = Question.objects.all().order_by('creation_date')
    context['reponses'] = QA_Answer.objects.all().order_by('creation_date')
    context['articles'] = QA_Article.objects.all().order_by('creation_date')
    context['experts'] = Profil.objects.filter(is_professional=True).values('user__email').annotate(
        nb_questions=Count('question', distinct=True), nb_reponses=Count('answer', distinct=True),
        nb_articles=Count('article', distinct=True)).exclude(
        Q(nb_questions=0) and Q(nb_reponses=0) and Q(nb_articles=0))
    context['membres_actifs'] = Profil.objects.all().values('user__email', 'user__last_name', 'user__first_name',
                                                            'points').exclude(points__lte=0).order_by('-points')[:8]
    context['nb_vues'] = Question.objects.aggregate(nb_vues=Sum('views_number'))['nb_vues'] + \
                         QA_Article.objects.aggregate(nb_vues=Sum('views'))['nb_vues']
    context['avg_reponse'] = \
        Question.objects.values('id').annotate(nb_rep=Count('answer')).aggregate(avg_reponse=Avg('nb_rep'))[
            'avg_reponse']

    context['questions_plus_vues'] = Question.objects.all().order_by('-views_number')[:10]
    context['articles_plus_vues'] = QA_Article.objects.all().order_by('-views')[:10]

    return render(request, "dashboard/qa/vue_generale.html", context)


## Questions ##
def qa_questions(request):
    if not admin_has_permission(groupe="QA", permission="Gérer les questions", request=request):
        return redirect("dashboard:index")

    context = {}

    context['questions'] = Question.objects.all().annotate(total_signals=Count('signalquestion'))

    return render(request, "dashboard/qa/lists/liste_questions.html", context)


# Questions ajax
def delete_questions(request):
    if not admin_has_permission(groupe="QA", permission="Gérer les questions", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune question sélectionnée.'})
    else:
        for id in ids:
            question = Question.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé la question  <strong>" + question.title + "</strong> posée par <strong>" + question.user.user.first_name.title() + " " + question.user.user.last_name.title() + "</strong> "
            action.save()

            question.delete()

        return JsonResponse({'status': 'success', 'message': 'Les questions sélectionnées ont été supprimées.'})


def qa_question(request, id_question):
    if not admin_has_permission(groupe="QA", permission="Gérer les questions", request=request):
        return redirect("dashboard:index")

    question = get_object_or_404(Question, id=id_question)

    context = {}

    context['question'] = question
    signalements = QA_SignalAnswer.objects.all().values('answer_id')

    signalements_answer_ids = []

    for signal in signalements:
        signalements_answer_ids.append(signal['answer_id'])

    context['signalements_answer_ids'] = signalements_answer_ids

    context['tracking_dernieres_visites'] = Tracker.objects.filter(model_name="Question",
                                                                   object_id=question.id).order_by('-timestamp')[:10]
    context['signalements'] = QA_SignalQuestion.objects.filter(question=question).count()

    return render(request, "dashboard/qa/infos/infos_question.html", context)


def delete_question(request, id_question):
    if not admin_has_permission(groupe="QA", permission="Gérer les questions", request=request):
        return redirect("dashboard:index")

    question = get_object_or_404(Question, id=id_question)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé la question  <strong>" + question.title + "</strong> posée par <strong>" + question.user.user.first_name.title() + " " + question.user.user.last_name.title() + "</strong> "
    action.save()

    question.delete()

    messages.success(request, "La question a été supprimée.")

    return redirect("dashboard:qa_questions")


def update_question(request, id_question):
    if not admin_has_permission(groupe="QA", permission="Gérer les questions", request=request):
        return redirect("dashboard:index")

    question = get_object_or_404(Question, id=id_question)

    context = {}

    form = FormModifierQuestion(instance=question)

    if request.method == "POST":
        form = FormModifierQuestion(request.POST, instance=question)
        if form.is_valid():
            form.save()

        admin = admin_logged(request)

        action = Action()
        action.date = timezone.now()
        action.admin = admin
        action.type = "Modification"
        action.nom = "A modifié la question  <strong>" + question.title + "</strong> posée par <strong>" + question.user.user.first_name.title() + " " + question.user.user.last_name.title() + "</strong> "
        action.save()

        messages.success(request, "La question a été modifiée.")

    context['form'] = form
    context['question'] = question

    return render(request, 'dashboard/qa/modifications/update_question.html', context)


def question_delete_signals(request, id_question):
    if not admin_has_permission(groupe="QA", permission="Gérer les questions", request=request):
        return redirect("dashboard:index")

    question = get_object_or_404(Question, id=id_question)
    signalements = QA_SignalQuestion.objects.filter(question=question)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé les signalements de la question  <strong>" + question.title + "</strong> posée par <strong>" + question.user.user.first_name.title() + " " + question.user.user.last_name.title() + "</strong> "
    action.save()

    if signalements.count() != 0:
        signalements.delete()

    messages.success(request, "Les signalements ont été supprimés.")

    return redirect("dashboard:qa_question", id_question=question.id)


## Réponses ##

def qa_reponses(request):
    if not admin_has_permission(groupe="QA", permission="Gérer les réponses", request=request):
        return redirect("dashboard:index")

    context = {}

    context['reponses'] = QA_Answer.objects.all().annotate(total_signals=Count('signalanswer'))

    return render(request, "dashboard/qa/lists/liste_reponses.html", context)


# Réponse ajax
def delete_reponses(request):
    if not admin_has_permission(groupe="QA", permission="Gérer les réponses", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune réponse sélectionnée.'})
    else:
        for id in ids:
            reponse = QA_Answer.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé la réponse  <strong>" + reponse.content[
                                                             :20] + "</strong> proposée par <strong>" + reponse.user.user.first_name.title() + " " + reponse.user.user.last_name.title() + "</strong> "
            action.save()

            reponse.delete()

        return JsonResponse({'status': 'success', 'message': 'Les réponses sélectionnées ont été supprimées.'})


def qa_reponse(request, id_reponse):
    if not admin_has_permission(groupe="QA", permission="Gérer les réponses", request=request):
        return redirect("dashboard:index")

    reponse = get_object_or_404(QA_Answer, id=id_reponse)

    context = {}

    context['reponse'] = reponse
    context['signal_question'] = QA_SignalQuestion.objects.filter(question=reponse.question).count()
    context['signal_reponse'] = QA_SignalAnswer.objects.filter(answer=reponse).count()

    return render(request, "dashboard/qa/infos/infos_reponse.html", context)


def delete_reponse(request, id_reponse):
    if not admin_has_permission(groupe="QA", permission="Gérer les réponses", request=request):
        return redirect("dashboard:index")

    reponse = get_object_or_404(QA_Answer, id=id_reponse)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé la réponse  <strong>" + reponse.content[
                                                     :20] + "</strong> proposée par <strong>" + reponse.user.user.first_name.title() + " " + reponse.user.user.last_name.title() + "</strong> "
    action.save()

    reponse.delete()

    messages.success(request, "La réponse a été supprimée.")

    return redirect("dashboard:qa_reponses")


def reponse_delete_signals(request, id_reponse):
    if not admin_has_permission(groupe="QA", permission="Gérer les questions", request=request):
        return redirect("dashboard:index")

    reponse = get_object_or_404(QA_Answer, id=id_reponse)
    signalements = QA_SignalAnswer.objects.filter(answer=reponse)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé les signalements de la  réponse <strong>" + reponse.content[
                                                                         :20] + "</strong> proposée par <strong>" + reponse.user.user.first_name.title() + " " + reponse.user.user.last_name.title() + "</strong> "
    action.save()

    if signalements.count() != 0:
        signalements.delete()

    messages.success(request, "Les signalements ont été supprimés.")

    return redirect("dashboard:qa_question", id_question=reponse.question.id)


def update_reponse(request, id_reponse):
    if not admin_has_permission(groupe="QA", permission="Gérer les réponses", request=request):
        return redirect("dashboard:index")

    reponse = get_object_or_404(QA_Answer, id=id_reponse)

    context = {}

    form = FormModifierReponse(instance=reponse)

    if request.method == "POST":
        form = FormModifierReponse(request.POST, instance=reponse)
        if form.is_valid():
            form.save()

        admin = admin_logged(request)

        action = Action()
        action.date = timezone.now()
        action.admin = admin
        action.type = "Modification"
        action.nom = "A modifié la réponse  <strong>" + reponse.content[
                                                        :20] + "</strong> proposée par <strong>" + reponse.user.user.first_name.title() + " " + reponse.user.user.last_name.title() + "</strong> "
        action.save()

        messages.success(request, "La réponse a été modifiée.")

    context['form'] = form
    context['reponse'] = reponse

    return render(request, 'dashboard/qa/modifications/update_reponse.html', context)


#### Categories ####


def qa_categories(request):
    if not admin_has_permission(groupe="QA", permission="Gérer les catégories", request=request):
        return redirect("dashboard:index")

    context = {}

    context['categories'] = QA_Category.objects.all()

    return render(request, "dashboard/qa/lists/liste_categories.html", context)


# Categories ajax
def qa_delete_categories(request):
    if not admin_has_permission(groupe="QA", permission="Gérer les catégories", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune catégorie sélectionnée.'})
    else:
        for id in ids:
            category = QA_Category.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé la catégorie QA  <strong>" + category.title + "</strong>"
            action.save()

            category.delete()

        return JsonResponse({'status': 'success', 'message': 'Les catégories sélectionnées ont été supprimées.'})


def qa_category_question(request, id_category):
    if not admin_has_permission(groupe="QA", permission="Gérer les catégories", request=request):
        return redirect("dashboard:index")

    category = get_object_or_404(QA_Category, id=id_category)

    context = {}

    context['category'] = category

    context['tracking_dernieres_visites'] = Tracker.objects.filter(model_name="QA Catégorie",
                                                                   object_id=category.id).order_by('-timestamp')[:10]

    return render(request, "dashboard/qa/infos/infos_categorie.html", context)


# Ajax Add Cat
def qa_add_category(request):
    if not admin_has_permission(groupe="QA", permission="Gérer les catégories", request=request):
        return redirect("dashboard:index")

    title = request.GET.get('title', None)
    description = request.GET.get('description', None)

    if not title or not description:
        return JsonResponse({'status': 'error', 'message': 'Les champs renseignés sont invalide.'})

    cat = QA_Category()
    cat.title = title
    cat.description = description
    cat.save()

    action = Action()
    action.date = timezone.now()
    action.admin = admin_logged(request)
    action.type = "Ajout"
    action.nom = "A ajouté la catégorie QA <strong>" + title + "</strong>"
    action.save()

    return JsonResponse({
        'status': 'success', 'message': 'Catégorie ajoutée avec succès.', 'id': cat.id,
    })


def qa_delete_category(request, id_category):
    if not admin_has_permission(groupe="QA", permission="Gérer les catégories", request=request):
        return redirect("dashboard:index")

    category = get_object_or_404(QA_Category, id=id_category)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé la catégorie QA <strong>" + category.title + "</strong>"
    action.save()

    category.delete()

    messages.success(request, "La catégorie a été supprimée.")

    return redirect("dashboard:qa_categories")


def qa_update_category(request, id_category):
    if not admin_has_permission(groupe="QA", permission="Gérer les catégories", request=request):
        return redirect("dashboard:index")

    category = get_object_or_404(QA_Category, id=id_category)

    context = {}

    form = FormModifierQACategorie(instance=category)

    if request.method == "POST":
        form = FormModifierQACategorie(request.POST, instance=category)
        if form.is_valid():
            cat = form.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A modifié la catégorie QA <strong>" + cat.title + "</strong> "
            action.save()

        messages.success(request, "La catégorie a été modifiée.")

    context['form'] = form
    context['category'] = category

    return render(request, 'dashboard/qa/modifications/update_category.html', context)


## Réponses ##

def qa_articles(request):
    if not admin_has_permission(groupe="QA", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    context = {}

    context['articles'] = QA_Article.objects.all().annotate(total_signals=Count('signalarticle'))

    return render(request, "dashboard/qa/lists/liste_articles.html", context)


# Réponse ajax
def qa_delete_articles(request):
    if not admin_has_permission(groupe="QA", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun article sélectionné.'})
    else:
        for id in ids:
            article = QA_Article.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé l'article QA  <strong>" + article.title[
                                                               :20] + "</strong> écrit par <strong>" + article.author.user.first_name.title() + " " + article.author.user.last_name.title() + "</strong> "
            action.save()

            article.delete()

        return JsonResponse({'status': 'success', 'message': 'Les articles sélectionnés ont été supprimés.'})


def qa_article(request, id_article):
    if not admin_has_permission(groupe="QA", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    article = get_object_or_404(QA_Article, id=id_article)

    context = {}

    context['article'] = article
    context['signalements'] = QA_SignalArticle.objects.filter(article=article).count()

    signalements = QA_SignalComment.objects.all().values('comment_id')

    signalements_comments_ids = []

    for signal in signalements:
        signalements_comments_ids.append(signal['comment_id'])

    context['signalements_comments_ids'] = signalements_comments_ids

    context['tracking_dernieres_visites'] = Tracker.objects.filter(model_name="QA Article",
                                                                   object_id=article.id).order_by('-timestamp')[:10]

    return render(request, "dashboard/qa/infos/infos_article.html", context)


def qa_delete_article(request, id_article):
    if not admin_has_permission(groupe="QA", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    article = get_object_or_404(QA_Article, id=id_article)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé l'article QA  <strong>" + article.title[
                                                       :20] + "</strong> écrit par <strong>" + article.author.user.first_name.title() + " " + article.author.user.last_name.title() + "</strong> "
    action.save()

    article.delete()

    messages.success(request, "L'article QA a été supprimée.")

    return redirect("dashboard:qa_articles")


def qa_update_article(request, id_article):
    if not admin_has_permission(groupe="QA", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    article = get_object_or_404(QA_Article, id=id_article)

    context = {}

    form = FormModifierQAArticle(instance=article)

    if request.method == "POST":
        form = FormModifierQAArticle(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A modifié l'article QA  <strong>" + article.title[
                                                              :20] + "</strong> écrit par <strong>" + article.author.user.first_name.title() + " " + article.author.user.last_name.title() + "</strong> "
            action.save()

            messages.success(request, "L'article a été modifiée.")

    form = FormModifierQAArticle(instance=article)

    context['form'] = form
    context['article'] = article

    return render(request, 'dashboard/qa/modifications/update_article.html', context)


## Experts ##

def qa_experts(request):
    if not admin_has_permission(groupe="QA", permission="Gérer les experts", request=request):
        return redirect("dashboard:index")

    context = {}

    context['experts'] = Profil.objects.filter(is_professional=True)

    return render(request, "dashboard/qa/lists/liste_experts.html", context)


def qa_signalements(request):
    context = {}

    signals_questions = QA_SignalQuestion.objects.all().extra(select={'type': 0})
    signals_answers = QA_SignalAnswer.objects.all().extra(select={'type': 1})
    signals_articles = QA_SignalArticle.objects.all().extra(select={'type': 2})
    signals_comments = QA_SignalComment.objects.all().extra(select={'type': 3})

    signalements = list(chain(signals_questions, signals_answers, signals_articles, signals_comments))
    signalements.sort(key=lambda x: x.creation_date, reverse=True)

    context['signalements'] = signalements

    return render(request, "dashboard/qa/lists/liste_signalements.html", context)


def qa_article_delete_signals(request, id):
    if not admin_has_permission(groupe="QA", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    article = get_object_or_404(QA_Article, id=id)
    signalements = QA_SignalArticle.objects.filter(article=article)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé les signalements de l'article <strong>" + article.title[
                                                                       :20] + "</strong> écrit par <strong>" + article.author.user.first_name.title() + " " + article.author.user.last_name.title() + "</strong> "
    action.save()

    if signalements.count() != 0:
        signalements.delete()

    messages.success(request, "Les signalements ont été supprimés.")

    return redirect("dashboard:qa_article", id_article=article.id)


def qa_comment_delete_signals(request, id):
    if not admin_has_permission(groupe="QA", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    comment = get_object_or_404(QA_Comment, id=id)
    signalements = QA_SignalComment.objects.filter(comment=comment)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé les signalements du commentaire <strong>" + comment.content[
                                                                         :20] + "</strong> l'article QA <strong>" + comment.article.title[
                                                                                                                    :20] + "</strong> écrit par <strong>" + comment.article.author.user.first_name.title() + " " + comment.article.author.user.last_name.title() + "</strong> "
    action.save()

    if signalements.count() != 0:
        signalements.delete()

    messages.success(request, "Les signalements ont été supprimés.")

    return redirect("dashboard:qa_article", id_article=comment.article.id)


def qa_delete_comment(request, id):
    if not admin_has_permission(groupe="QA", permission="Gérer les articles", request=request):
        return redirect("dashboard:index")

    comment = get_object_or_404(QA_Comment, id=id)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé le commentaire <strong>" + comment.content[
                                                        :20] + "</strong> l'article QA <strong>" + comment.article.title[
                                                                                                   :20] + "</strong> écrit par <strong>" + comment.article.author.user.first_name.title() + " " + comment.article.author.user.last_name.title() + "</strong> "
    action.save()

    comment.delete()

    messages.success(request, "Le commentaire a été supprimé.")

    return redirect("dashboard:qa_article", id_article=comment.article.id)


# Signalements ajax
def qa_delete_signalements(request):
    admin = admin_logged(request)
    signals = request.GET.getlist('ids[]', None)

    if not signals or signals is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun signalement sélectionnée.'})
    else:
        for signall in signals:
            signal = json.loads(signall)
            print(signal['type'])

            message = ""

            if signal['type'] == "0":  # Question
                signal_question = QA_SignalQuestion.objects.get(id=signal['id'])
                message = "A supprimé le signalements de la question  <strong>" + signal_question.question.title + "</strong> posée par <strong>" + signal_question.question.user.user.first_name.title() + " " + signal_question.question.user.user.last_name.title() + "</strong> "
                signal_question.delete()
            elif signal['type'] == "1":  # Réponse
                signal_reponse = QA_SignalAnswer.objects.get(id=signal['id'])
                message = "A supprimé le signalements de la  réponse <strong>" + signal_reponse.answer.content[
                                                                                 :20] + "</strong> proposée par <strong>" + signal_reponse.answer.user.user.first_name.title() + " " + signal_reponse.answer.user.user.last_name.title() + "</strong> "
                signal_reponse.delete()
            elif signal['type'] == "2":  # Article
                signal_article = QA_SignalArticle.objects.get(id=signal['id'])
                message = "A supprimé le signalement de l'article QA  <strong>" + signal_article.article.title[
                                                                                  :20] + "</strong> écrit par <strong>" + signal_article.article.author.user.first_name.title() + " " + signal_article.article.author.user.last_name.title() + "</strong> "
                signal_article.delete()
            elif signal['type'] == "3":  # Commentaire
                signal_comment = QA_SignalComment.objects.get(id=signal['id'])
                message = "A supprimé le signalement d'un commentaire sur l'article QA  <strong>" + signal_comment.comment.article.title[
                                                                                                    :20] + "</strong> écrit par <strong>" + signal_comment.comment.article.author.user.first_name.title() + " " + signal_comment.comment.article.author.user.last_name.title() + "</strong> "
                signal_comment.delete()

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = message
            action.save()

        return JsonResponse({'status': 'success', 'message': 'Les signalements sélectionnés ont été supprimés.'})


########### END Q and A ###########


############ DEBUT AO ############


from ao.models import Company, AOUser, AO, Project, AOSaves, PSaves, Quotation, Contact as AO_Contact


def ao_general_view(request):
    if not admin_has_permission(groupe="AO", permission="Vue d'ensemble", request=request):
        return redirect("dashboard:index")

    context = {}

    context['profils_entreprises'] = Company.objects.all()[:10]
    context['appels_offres'] = AO.objects.all()[:10]
    context['lots'] = Project.objects.all()[:10]
    context['devis'] = Quotation.objects.all()[:10]

    context['nb_profils_entreprises'] = Company.objects.all().count()
    context['nb_appels_offres'] = AO.objects.all().count()
    context['nb_lots'] = Project.objects.all().count()
    context['nb_devis'] = Quotation.objects.all().count()

    try:
        vues = AO.objects.aggregate(total_views=Sum('views'))['total_views'] + \
               Project.objects.aggregate(total_views=Sum('views'))['total_views']
    except:
        vues = 0

    context['vues'] = vues
    context['nb_contacts'] = AO_Contact.objects.all().count()

    return render(request, "dashboard/ao/vue_generale.html", context)


## Profils Entreprise ##
def ao_profils_entreprises(request):
    if not admin_has_permission(groupe="AO", permission="Gérer les profils entreprises", request=request):
        return redirect("dashboard:index")

    context = {}

    context['profils_entreprises'] = Company.objects.all()

    return render(request, "dashboard/ao/lists/liste_profils_entreprises.html", context)


## Profil Entreprise ##
def ao_profil_entreprise(request, id):
    if not admin_has_permission(groupe="AO", permission="Gérer les profils entreprises", request=request):
        return redirect("dashboard:index")

    context = {}

    profilent = get_object_or_404(Company, id=id)
    appels_offres = profilent.aouser().ao_set.all()

    context['profilent'] = profilent
    context['appels_offres'] = appels_offres
    context['lots'] = Project.objects.filter(ao__in=appels_offres)
    context['ao_saves'] = AOSaves.objects.filter(user=profilent.aouser())
    context['p_saves'] = PSaves.objects.filter(user=profilent.aouser())

    return render(request, "dashboard/ao/infos/infos_profil_entreprise.html", context)


def ao_delete_profil_entreprise(request, id):
    if not admin_has_permission(groupe="AO", permission="Gérer les profils entreprises", request=request):
        return redirect("dashboard:index")

    profilent = get_object_or_404(Company, id=id)
    aouser = AOUser.objects.filter(company=profilent)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé le profile de l'entreprise (AO) <strong>" + profilent.name[
                                                                         :20] + "</strong> de l'utilisateur <strong>" + profilent.aouser().user.first_name.title() + " " + profilent.aouser().user.last_name.title() + "</strong> "
    action.save()

    profilent.delete()
    aouser.delete()

    messages.success(request, "Le profil de l'entreprise a été supprimé.")

    return redirect("dashboard:ao_profils_entreprises")


def ao_update_profil_entreprise(request, id):
    if not admin_has_permission(groupe="AO", permission="Gérer les profils entreprises", request=request):
        return redirect("dashboard:index")

    profilent = get_object_or_404(Company, id=id)

    context = {}

    form_profilent = FormModifierProfilEntreprise(instance=profilent)

    if request.method == "POST":
        form_profilent = FormModifierProfilEntreprise(request.POST, request.FILES, instance=profilent)

        if form_profilent.is_valid():
            form_profilent.save()
            messages.success(request, "Le profil de l'entreprise a été modifié avec succès.")

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié la boutique <strong> " + profilent.name + "</strong>"
            action.save()
        else:
            print(form_profilent.errors)

    context['profilent'] = profilent
    context['form_profilent'] = form_profilent

    return render(request, 'dashboard/ao/modifications/update_profil_entreprise.html', context)


# Profils Entreprise ajax
def ao_delete_profils_entreprises(request):
    if not admin_has_permission(groupe="AO", permission="Gérer les profils entreprises", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun profil d\'entreprise sélectionné.'})
    else:
        for id in ids:
            company = Company.objects.get(id=id)
            aouser = AOUser.objects.filter(company=company)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé le profil d'entreprise  <strong>" + company.name + "</strong> de l'utilisateur par <strong>" + company.aouser().user.first_name.title() + " " + company.aouser().user.last_name.title() + "</strong> "
            action.save()

            company.delete()
            aouser.delete()

        return JsonResponse({'status': 'success', 'message': 'Les profils d\'entreprises ont été supprimés.'})


## Lots ##
def ao_lots(request):
    if not admin_has_permission(groupe="AO", permission="Gérer les lots", request=request):
        return redirect("dashboard:index")

    context = {}

    context['lots'] = Project.objects.all()

    return render(request, "dashboard/ao/lists/liste_lots.html", context)


## Lot ##
def ao_lot(request, id):
    if not admin_has_permission(groupe="AO", permission="Gérer les lots", request=request):
        return redirect("dashboard:index")

    context = {}

    lot = get_object_or_404(Project, id=id)

    context['lot'] = lot

    return render(request, "dashboard/ao/infos/infos_lot.html", context)


def ao_delete_lot(request, id):
    if not admin_has_permission(groupe="AO", permission="Gérer les lots", request=request):
        return redirect("dashboard:index")

    lot = get_object_or_404(Project, id=id)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé le lot d'offre <strong>" + lot.title + "</strong> de  <strong>" + lot.ao.company() + "</strong>"
    action.save()

    lot.delete()

    messages.success(request, "Le lot a été supprimé.")

    return redirect("dashboard:ao_lots")


def ao_update_lot(request, id):
    if not admin_has_permission(groupe="AO", permission="Gérer les lots", request=request):
        return redirect("dashboard:index")

    lot = get_object_or_404(Project, id=id)

    context = {}

    form = FormModifierLot(instance=lot)

    if request.method == "POST":
        form = FormModifierLot(request.POST, instance=lot)

        if form.is_valid():
            ao = form.save()
            messages.success(request, "Le lot a été modifié avec succès.")

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié le lot <strong> " + lot.title + "</strong> de <strong>" + lot.ao.company() + " </strong>"
            action.save()

            if ao.get_interested_mails():
                sujet = "Un changement a été effectué à l'appel d'offre qui vous interesse"
                send_multiple_mails(emails_addresses=ao.get_interested_mails(), sujet=sujet, message=sujet,
                                    request=request, object_=ao, type_='lot', company=None)


        else:
            print(form.errors)

    context['form'] = form
    context['lot'] = lot

    return render(request, 'dashboard/ao/modifications/update_lot.html', context)


# Profils Entreprise ajax
def ao_delete_lots(request):
    if not admin_has_permission(groupe="AO", permission="Gérer les lots", request=request):
        return redirect("dashboard:index")

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun lot sélectionné.'})
    else:
        for id in ids:
            lot = get_object_or_404(Project, id=id)

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé le lot <strong>" + lot.title + "</strong> de l'entreprise  <strong>" + lot.ao.get_company().name[
                                                                                                            :20] + "</strong> de l'utilisateur <strong>" + lot.ao.get_company().aouser().user.first_name.title() + " " + lot.ao.get_company().aouser().user.last_name.title() + "</strong> "
            action.save()

            lot.delete()

        return JsonResponse({'status': 'success', 'message': 'Les lots ont été supprimés.'})


def ao_delete_appel_offre(request, id):
    if not admin_has_permission(groupe="AO", permission="Gérer les appels d'offres", request=request):
        return redirect("dashboard:index")

    ao = get_object_or_404(AO, id=id)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé l'appel d'offre <strong>" + ao.title + "</strong> de l'entreprise <strong>" + ao.company() + "</strong>"
    action.save()

    ao.delete()

    messages.success(request, "L'appel d'offre a été supprimée.")

    return redirect("dashboard:ao_appels_offres")


def ao_update_appel_offre(request, id):
    if not admin_has_permission(groupe="AO", permission="Gérer les appels d'offres", request=request):
        return redirect("dashboard:index")

    ao = get_object_or_404(AO, id=id)

    context = {}

    form = FormModifierAO(instance=ao)

    if request.method == "POST":
        form = FormModifierAO(request.POST, request.FILES, instance=ao)
        if form.is_valid():
            form.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A modifié l'appel d'offre <strong>" + ao.title + "</strong> de  <strong>" + ao.company() + "</strong> "
            action.save()

            if ao.get_interested_mails():
                sujet = "Un changement a été effectué à l'appel d'offre qui vous interesse"
                send_multiple_mails(emails_addresses=ao.get_interested_mails(), sujet=sujet, message=sujet,
                                    request=request, object_=ao, type_='ao', company=None)

            messages.success(request, "L'appel d'offre a été modifiée.")

    form = FormModifierAO(instance=ao)

    context['form'] = form
    context['offre'] = ao

    return render(request, 'dashboard/ao/modifications/update_appel_offre.html', context)


## Appels Offres ##
def ao_appels_offres(request):
    if not admin_has_permission(groupe="AO", permission="Gérer les appels d'offres", request=request):
        return redirect("dashboard:index")

    context = {}

    context['appels_offres'] = AO.objects.all()

    return render(request, "dashboard/ao/lists/liste_appels_offres.html", context)


from ao.models import Company, AOUser, AO, Project, AOSaves, PSaves, TVA, QuotationNbRows


## Profil Entreprise ##
def ao_appel_offre(request, id):
    if not admin_has_permission(groupe="AO", permission="Gérer les appels d'offres", request=request):
        return redirect("dashboard:index")

    context = {}

    offre = get_object_or_404(AO, id=id)

    context['offre'] = offre

    return render(request, "dashboard/ao/infos/infos_appel_offre.html", context)


def ao_delete_ao(request, id):
    if not admin_has_permission(groupe="AO", permission="Gérer les appels d'offres", request=request):
        return redirect("dashboard:index")

    ao = get_object_or_404(AO, id=id)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé l'appel d'offre <strong>" + ao.title + "</strong> de  <strong>" + ao.company() + "</strong> de l'utilisateur <strong>" + ao.user.user.first_name.title() + " " + ao.user.user.last_name.title() + "</strong> "
    action.save()

    ao.delete()

    messages.success(request, "L'appel d'offre a été supprimée.")

    return redirect("dashboard:ao_appels_offres")


def ao_delete_aos(request):
    if not admin_has_permission(groupe="AO", permission="Gérer les appels d'offres", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune appel d\'offre sélectionné.'})
    else:
        for id in ids:
            ao = get_object_or_404(AO, id=id)

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé l'appel d'offre <strong>" + ao.title + "</strong> de l'entreprise  <strong>" + ao.company() + "</strong> de l'utilisateur <strong>" + ao.user.user.first_name.title() + " " + ao.user.user.last_name.title() + "</strong> "
            action.save()

            ao.delete()

        return JsonResponse({'status': 'success', 'message': 'Les appels d\'offres ont été supprimés.'})


## / Devis ##

def ao_devis(request):
    if not admin_has_permission(groupe="AO", permission="Gérer les devis", request=request):
        return redirect("dashboard:index")

    context = {}

    context['deviss'] = Quotation.objects.all()

    return render(request, "dashboard/ao/lists/liste_devis.html", context)


## Profil Entreprise ##
def ao_devis_one(request, id):
    if not admin_has_permission(groupe="AO", permission="Gérer les devis", request=request):
        return redirect("dashboard:index")

    context = {}

    devis = get_object_or_404(Quotation, id=id)

    context['devis'] = devis
    context['total'] = Quotation.objects.filter(id=id).aggregate(total=Sum('quotationline__price'))['total']

    return render(request, "dashboard/ao/infos/infos_devis.html", context)


def ao_delete_devis(request, id):
    if not admin_has_permission(groupe="AO", permission="Gérer les devis", request=request):
        return redirect("dashboard:index")

    devis = get_object_or_404(Quotation, id=id)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé le devis  de l'entreprise  <strong>" + devis.ao.company() + "</strong> sur l'appel d'offre <strong>" + devis.ao.title + "</strong>"
    action.save()

    devis.delete()

    messages.success(request, "Le devis a été supprimé.")

    return redirect("dashboard:ao_devis")


def ao_delete_devis_list(request):
    if not admin_has_permission(groupe="AO", permission="Gérer les devis", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun devis d\'offre sélectionné.'})
    else:
        for id in ids:
            devis = get_object_or_404(Quotation, id=id)

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé le devis  de l'entreprise  <strong>" + devis.ao.company() + "</strong> sur l'appel d'offre <strong>" + devis.ao.title + "</strong>"
            action.save()

            devis.delete()

        return JsonResponse({'status': 'success', 'message': 'Les devis ont été supprimés.'})


####  AO PARAMETRES ##

def ao_parametres(request):
    if not admin_has_permission(groupe="AO", permission="Gérer les parametres", request=request):
        return redirect("dashboard:index")

    context = {}
    context['tvas'] = TVA.objects.all()

    # Si c'est POST   alors on a submit leformulaire de nb rows quotation
    if request.method == "POST":
        nb_lignes = request.POST.get('quotation_nb_rows', None)

        if nb_lignes:
            # S'il n'est pas entier on donne un msg d'erreur et change pas la valeur
            try:
                int(nb_lignes)
                QuotationNbRows.update_value(nb_lignes)
                messages.success(request, "La valeur du nombre  de  lignes du devis a été changée avec succès.")
            except ValueError:
                messages.error(request, "La valeur du nombre  de  lignes du devis est erronée. Veuillez réessayer.")

    context['quotation_nb_rows'] = QuotationNbRows.get_value()

    return render(request, 'dashboard/ao/parametres.html', context)


def ao_delete_tva(request, id):
    if not admin_has_permission(groupe="AO", permission="Gérer les parametres", request=request):
        return redirect("dashboard:index")

    tva = get_object_or_404(TVA, id=id)
    tva.delete()

    messages.success(request, "Le taux de TVA a  été supprimé.")

    return redirect('dashboard:ao_parametres')


def ao_add_tva(request):
    if not admin_has_permission(groupe="AO", permission="Gérer les parametres", request=request):
        return redirect("dashboard:index")

    if request.method == "POST":
        taux_tva = request.POST.get('taux_tva', None)

        if taux_tva:
            # S'il n'est pas entier on donne un msg d'erreur et change pas la valeur
            try:
                int(taux_tva)
                tva = TVA()
                tva.tva = taux_tva
                tva.save()

                messages.success(request, "Le taux de TVA a  été ajouté.")
            except ValueError:
                messages.error(request, "La valeur du taux de TVA est erronée. Veuillez réessayer.")

    messages.success(request, "Le taux de TVA a  été ajouté.")

    return redirect('dashboard:ao_parametres')


def ao_profils_particuliers(request):
    if not admin_has_permission(groupe="AO", permission="Gérer les utilisateurs", request=request):
        return redirect("dashboard:index")

    context = {}

    aousers = AOUser.objects.all().values('user__id')
    context['profils'] = Profil.objects.all().exclude(id__in=aousers)

    return render(request, 'dashboard/ao/lists/liste_particuliers.html', context)


def parametres(request):
    if not admin_has_permission(groupe="AO", permission="Gérer les parametres", request=request):
        return redirect("dashboard:index")

    context = {}

    # Si c'est POST   alors on a submit leformulaire de nb rows quotation
    if request.method == "POST":
        if request.POST.get('activer_langue', False):
            langue = True
        else:
            langue = False

        email_host = request.POST.get('email_host', None)
        email_host_user = request.POST.get('email_host_user', None)
        email_host_password = request.POST.get('email_host_password', None)
        email_port = request.POST.get('email_port', None)
        titre_site = request.POST.get('titre_site', None)

        if email_host and email_host_user and email_host_password and email_port and titre_site:
            # S'il n'est pas entier on donne un msg d'erreur et change pas la valeur
            print("hey")
            try:
                Parameters.update_object(langue, email_host, email_host_user, email_host_password, email_port,
                                         titre_site)
                print("ok success")
                messages.success(request, "Les paramètres ont  été  changés avec succès.")
            except ValueError:
                messages.error(request, "Une erreur s'est produite.")
                print("not ok  ERROR ")
        else:
            print("h88h")

    context['parametres'] = Parameters.get_object()

    return render(request, 'dashboard/parametres.html', context)


########################### Elearning

# Demandes Professeurs ###########################

def elearning_general_view(request):
    if not admin_has_permission(groupe="Elearning", permission="Vue d'ensemble", request=request):
        return redirect("dashboard:index")
    context = {}

    # Ventes ces 12 derniers mois
    last_seven_months = datetime.today() - timedelta(days=365)  # last 365 days
    ventes = OrderLine.objects.filter(order__date__gt=last_seven_months).annotate(
        month=ExtractMonth('order__date')).values('month').annotate(total_ventes=Sum('total')).order_by()

    context['nb_boutiques'] = Shop.objects.filter(approved=True).count()
    context['nb_produits'] = Product.objects.filter(approved=True).count()
    context['prix_ventes'] = Order.objects.all().aggregate(total_ventes=Sum('amount'))['total_ventes']
    context['commandes'] = Order.objects.all()
    context['demandes_devis'] = MessageSupplier.objects.count()
    context['ventes'] = ventes
    context['produits'] = Product.objects.filter(approved=False).reverse()[:7]
    context['exposants_requests'] = Shop.objects.filter(approved=False).reverse()[:7]
    context['cart'] = Cart.objects.all().count()
    context['wish'] = WishList.objects.all().count()
    context['produits_plus_visites'] = Product.objects.all().order_by('-number_views')[:10]
    context['boutiques_plus_visites'] = Shop.objects.all().order_by('-number_visitors')[:10]
    context['produits_plus_recherches'] = Product.objects.all().annotate(total_search=Count('resultsearch')).order_by(
        '-total_search')[:10]

    print(context['produits_plus_recherches'])

    return render(request, 'dashboard/elearning/vue_generale.html', context)


def elearning_demandes_professeurs(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les professeurs", request=request):
        return redirect("dashboard:index")

    context = {}

    context['profils_demandeurs'] = Profil.objects.filter(request_teacher=True,is_teacher=False)

    return render(request, 'dashboard/elearning/lists/demandes_professeurs.html', context)


def elearning_delete_demandes_professeurs(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les professeurs", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune demande sélectionnée.'})
    else:
        for id in ids:
            demande_to_delete = Profil.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A refusé la demande à  devenir professeur de <strong>" + demande_to_delete.user.get_full_name().title() + "</strong>"
            action.save()

            demande_to_delete.request_teacher = False
            demande_to_delete.save()

        return JsonResponse({'status': 'success', 'message': 'Les demandes sélectionnées ont été supprimées.'})


def elearning_approve_demandes_professeurs(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les professeurs", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune demande sélectionnée.'})
    else:
        for id in ids:
            demande_to_delete = Profil.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A approuvé la demande à devenir professeur de <strong>" + demande_to_delete.user.get_full_name().title() + "</strong>"
            action.save()

            demande_to_delete.request_teacher = False
            demande_to_delete.is_teacher = True
            demande_to_delete.save()

        return JsonResponse({'status': 'success', 'message': 'Les demandes sélectionnées ont été approuvées.'})

# Professeurs

def elearning_professeurs(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les professeurs", request=request):
        return redirect("dashboard:index")

    context = {}

    context['profils'] = Profil.objects.filter(is_teacher=True,request_teacher=False).annotate(total_views=Sum('elearning_course_set__view'),total_share=Sum('elearning_course_set__share'))

    return render(request, 'dashboard/elearning/lists/professeurs.html', context)


def elearning_delete_statut_professeur(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les professeurs", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun professeur sélectionnée.'})
    else:
        for id in ids:
            demande_to_delete = Profil.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A retiré le statut de professeur à <strong>" + demande_to_delete.user.get_full_name().title() + "</strong>"
            action.save()

            demande_to_delete.request_teacher = False
            demande_to_delete.is_teacher = False
            demande_to_delete.save()

        return JsonResponse({'status': 'success', 'message': 'Les profils selectionnés ne sont plus professeur.'})

#  Categories


def elearning_categories(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les catégories", request=request):
        return redirect("dashboard:index")

    context = {}

    context['categories'] = Elearning_Category.objects.all()

    return render(request, "dashboard/elearning/lists/categories.html", context)


# Categories ajax
def elearning_delete_categories(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les catégories", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune catégorie sélectionnée.'})
    else:
        for id in ids:
            category = Elearning_Category.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé la catégorie Elearning  <strong>" + category.name + "</strong>"
            action.save()

            category.delete()

        return JsonResponse({'status': 'success', 'message': 'Les catégories sélectionnées ont été supprimées.'})


def elearning_add_category(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les catégories", request=request):
        return redirect("dashboard:index")

    context = {}

    form = FormElearningCategory(request.POST or None,request.FILES or None)

    if request.method == "POST":
        if form.is_valid():
            cat = form.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Ajout"
            action.nom = "A ajouté la catégorie Elearning <strong>" + cat.name + "</strong> "
            action.save()
            form = FormElearningCategory()

        messages.success(request, "La catégorie a été ajoutée.")

    context['form'] = form

    return render(request, 'dashboard/elearning/add/add_category.html', context)


def elearning_delete_category(request, id_category):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les catégories", request=request):
        return redirect("dashboard:index")

    category = get_object_or_404(Elearning_Category, id=id_category)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé la catégorie Elearning <strong>" + category.name + "</strong>"
    action.save()

    category.delete()

    messages.success(request, "La catégorie a été supprimée.")

    return redirect("dashboard:elearning_categories")


def elearning_update_category(request, id_category):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les catégories", request=request):
        return redirect("dashboard:index")

    category = get_object_or_404(Elearning_Category, id=id_category)

    context = {}

    form = FormElearningCategory(request.POST or None,request.FILES or None,instance=category  )

    if request.method == "POST":
        if form.is_valid():
            cat = form.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A modifié la catégorie Elearning <strong>" + cat.name + "</strong> "
            action.save()
            form = FormElearningCategory()

        messages.success(request, "La catégorie a été modifiée.")

    context['form'] = form
    context['category'] = category

    return render(request, 'dashboard/elearning/modification/update_category.html', context)


# Sous catégories

def elearning_sub_categories(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les sous catégories", request=request):
        return redirect("dashboard:index")

    context = {}

    context['categories'] = Elearning_SubCategory.objects.all()

    return render(request, "dashboard/elearning/lists/sub_categories.html", context)


# Categories ajax
def elearning_delete_sub_categories(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les sous catégories", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune sous-catégorie sélectionnée.'})
    else:
        for id in ids:
            category = Elearning_SubCategory.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé la sous-catégorie Elearning  <strong>" + category.name + "</strong>"
            action.save()

            category.delete()

        return JsonResponse({'status': 'success', 'message': 'Les sous-catégories sélectionnées ont été supprimées.'})


def elearning_add_sub_category(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les sous catégories", request=request):
        return redirect("dashboard:index")

    context = {}

    form = FormElearningSubCategory(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            cat = form.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Ajout"
            action.nom = "A ajouté la sous-catégorie Elearning <strong>" + cat.name + "</strong> "
            action.save()
            form = FormElearningSubCategory()

        messages.success(request, "La sous-catégorie a été ajoutée.")

    context['form'] = form

    return render(request, 'dashboard/elearning/add/add_sub_category.html', context)


def elearning_delete_sub_category(request, id_category):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les sous catégories", request=request):
        return redirect("dashboard:index")

    category = get_object_or_404(Elearning_SubCategory, id=id_category)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé la sous-atégorie Elearning <strong>" + category.name + "</strong>"
    action.save()

    category.delete()

    messages.success(request, "La sous-catégorie a été supprimée.")

    return redirect("dashboard:elearning_sub_categories")


def elearning_update_sub_category(request, id_category):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les sous catégories", request=request):
        return redirect("dashboard:index")

    category = get_object_or_404(Elearning_SubCategory, id=id_category)

    context = {}

    form = FormElearningSubCategory(request.POST or None,instance=category )

    if request.method == "POST":
        if form.is_valid():
            cat = form.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A modifié la sous-catégorie Elearning <strong>" + cat.name + "</strong> "
            action.save()

        messages.success(request, "La sous-catégorie a été modifiée.")

    context['form'] = form
    context['category'] = category

    return render(request, 'dashboard/elearning/modification/update_sub_category.html', context)


### Cours


def elearning_cours(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    context = {}

    context['courses'] = Elearning_Course.objects.all()

    return render(request, "dashboard/elearning/lists/cours.html", context)


# Cours ajax
def elearning_delete_cours(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun cours sélectionné.'})
    else:
        for id in ids:
            cours = Elearning_Course.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé le cours Elearning  <strong>" + cours.name + "</strong>"
            action.save()

            cours.delete()

        return JsonResponse({'status': 'success', 'message': 'Les cours sélectionnés ont été supprimés.'})


def elearning_approve_cours(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun cours sélectionné.'})
    else:
        for id in ids:
            cours = Elearning_Course.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A approuvé le cours Elearning <strong>" + cours.name + "</strong>"
            action.save()

            cours.to_evaluate = False
            cours.approved = True
            cours.save()

        return JsonResponse({'status': 'success', 'message': 'Les cours sélectionnés ont été approuvés.'})


def elearning_deapprove_cours(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun cours sélectionné.'})
    else:
        for id in ids:
            cours = Elearning_Course.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A désapprouvé le cours Elearning <strong>" + cours.name + "</strong>"
            action.save()

            cours.approved = False
            cours.save()

        return JsonResponse({'status': 'success', 'message': 'Les cours sélectionnés ont été désapprouvés.'})


def elearning_active_cours(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun cours sélectionné.'})
    else:
        for id in ids:
            cours = Elearning_Course.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A activé le cours Elearning <strong>" + cours.name + "</strong>"
            action.save()

            cours.active = True
            cours.save()

        return JsonResponse({'status': 'success', 'message': 'Les cours sélectionnés ont été activés.'})


def elearning_deactive_cours(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun cours sélectionné.'})
    else:
        for id in ids:
            cours = Elearning_Course.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A désactivé le cours Elearning <strong>" + cours.name + "</strong>"
            action.save()

            cours.active = False
            cours.save()

        return JsonResponse({'status': 'success', 'message': 'Les cours sélectionnés ont été désactivés.'})



## Cours  ##
def elearning_infos_cours(request, id):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    context = {}

    cours = get_object_or_404(Elearning_Course, id=id)

    context['cours'] = cours

    return render(request, "dashboard/elearning/infos/course.html", context)


def elearning_delete_cours(request, id):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    cours = get_object_or_404(Elearning_Course, id=id)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé le cours <strong>" + cours.name + "</strong>"
    action.save()

    cours.delete()

    messages.success(request, "Le cours a été supprimé.")

    return redirect("dashboard:elearning_cours")


def elearning_update_cours(request, id):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    cours = get_object_or_404(Elearning_Course, id=id)

    context = {}

    form = FormElearningCours(request.POST or None, request.FILES or None, instance=cours)

    if request.method == "POST":

        if form.is_valid():
            cours = form.save()
            messages.success(request, "Le cours a été modifié avec succès.")

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié le cours <strong> " + cours.name + "</strong>"
            action.save()

    context['form'] = form
    context['cours'] = cours

    return render(request, 'dashboard/elearning/modification/update_cours.html', context)

# Prerequis


def elearning_add_prerequis(request, id):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    context = {}

    cours = get_object_or_404(Elearning_Course,id=id)

    form = FormElearningPrerequis(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            prerequis = form.save(commit=False)
            prerequis.course = cours
            prerequis.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Ajout"
            action.nom = "A ajouté le prérequis <strong>" + prerequis.value + "</strong> pour le cours <strong>" +prerequis.course.name+ "</strong>"
            action.save()

            messages.success(request, "Le prérequis a été ajouté avec succès.")

            return redirect("dashboard:elearning_infos_cours", id=prerequis.course.id)


        messages.success(request, "Le prérequis a été ajouté.")

    context['form'] = form
    context['cours'] = cours

    return render(request, 'dashboard/elearning/add/add_prerequis.html', context)


def elearning_update_prerequis(request, id_prerequis):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    prerequis = get_object_or_404(Elearning_Prerequisites, id=id_prerequis)

    context = {}

    form = FormElearningPrerequis(request.POST or None, request.FILES or None, instance=prerequis)

    if request.method == "POST":

        if form.is_valid():
            cours = form.save()
            messages.success(request, "Le prérequis a été modifié avec succès.")

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié le prérequis <strong>" + prerequis.value + "</strong> pour le cours <strong>" +prerequis.course.name+ "</strong>"
            action.save()

            return redirect("dashboard:elearning_infos_cours", id=prerequis.course.id)

    context['form'] = form
    context['prerequis'] = prerequis

    return render(request, 'dashboard/elearning/modification/update_prerequis.html', context)


def elearning_delete_prerequis(request, id_prerequis):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    prerequis = get_object_or_404(Elearning_Prerequisites, id=id_prerequis)
    course_id = prerequis.course.id

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé le prérequis <strong>" + prerequis.value + "</strong> pour le cours <strong>" +prerequis.course.name+ "</strong>"
    action.save()

    prerequis.delete()

    messages.success(request, "Le prérequis a été supprimé.")

    return redirect("dashboard:elearning_infos_cours", id=course_id)


# Post Skills

def elearning_add_postskill(request, id):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    context = {}

    cours = get_object_or_404(Elearning_Course,id=id)

    form = FormElearningPostSkill(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            postskill = form.save(commit=False)
            postskill.course = cours
            postskill.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Ajout"
            action.nom = "A ajouté le postskill <strong>" + postskill.value + "</strong> pour le cours <strong>" +postskill.course.name+ "</strong>"
            action.save()

            messages.success(request, "Le postskill a été ajouté avec succès.")

            return redirect("dashboard:elearning_infos_cours", id=postskill.course.id)


    context['form'] = form
    context['cours'] = cours

    return render(request, 'dashboard/elearning/add/add_postskill.html', context)


def elearning_update_postskill(request, id_postskill):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    postskill = get_object_or_404(Elearning_PostSkills, id=id_postskill)

    context = {}

    form = FormElearningPostSkill(request.POST or None, request.FILES or None, instance=postskill)

    if request.method == "POST":

        if form.is_valid():
            postskill = form.save()
            messages.success(request, "Le postskill a été modifié avec succès.")

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié le prérequis <strong>" + postskill.value + "</strong> pour le cours <strong>" +postskill.course.name+ "</strong>"
            action.save()

            return redirect("dashboard:elearning_infos_cours", id=postskill.course.id)

    context['form'] = form
    context['postskill'] = postskill

    return render(request, 'dashboard/elearning/modification/update_postskill.html', context)


def elearning_delete_postskill(request, id_postskill):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    postskill = get_object_or_404(Elearning_PostSkills, id=id_postskill)
    course_id = postskill.course.id

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé le PostSkill <strong>" + postskill.value + "</strong> pour le cours <strong>" +postskill.course.name+ "</strong>"
    action.save()

    postskill.delete()

    messages.success(request, "Le postskill a été supprimé.")

    return redirect("dashboard:elearning_infos_cours", id=course_id)

# Chapitres


def elearning_add_chapter(request, id):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    context = {}

    cours = get_object_or_404(Elearning_Course,id=id)

    form = FormElearningChapitre(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.course = cours
            chapter.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Ajout"
            action.nom = "A ajouté le chapitre <strong>" + chapter.name + "</strong> pour le cours <strong>" +chapter.course.name+ "</strong>"
            action.save()

            messages.success(request, "Le chapitre a été ajouté avec succès.")

            return redirect("dashboard:elearning_infos_cours", id=chapter.course.id)


    context['form'] = form
    context['cours'] = cours

    return render(request, 'dashboard/elearning/add/add_chapter.html', context)


def elearning_update_chapter(request, id_chapter):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    chapter = get_object_or_404(Elearning_Part, id=id_chapter)

    context = {}

    form = FormElearningChapitre(request.POST or None, request.FILES or None, instance=chapter)

    if request.method == "POST":

        if form.is_valid():
            chapter = form.save()
            messages.success(request, "Le chapitre a été modifié avec succès.")

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié le chapitre <strong>" + chapter.name + "</strong> pour le cours <strong>" +chapter.course.name+ "</strong>"
            action.save()

            return redirect("dashboard:elearning_infos_cours", id=chapter.course.id)

    context['form'] = form
    context['chapter'] = chapter

    return render(request, 'dashboard/elearning/modification/update_chapter.html', context)


def elearning_delete_chapter(request, id_chapter):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    chapter = get_object_or_404(Elearning_Part, id=id_chapter)
    course_id = chapter.course.id

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé le chapitre <strong>" + chapter.name + "</strong> pour le cours <strong>" +chapter.course.name+ "</strong>"
    action.save()

    chapter.delete()

    messages.success(request, "Le chapitre a été supprimé.")

    return redirect("dashboard:elearning_infos_cours", id=course_id)


# Leçons

def elearning_add_lecon(request, id_chapitre):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    context = {}

    chapitre = get_object_or_404(Elearning_Part,id=id_chapitre)
    cours = chapitre.course

    form = FormElearningLecon(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            lecon = form.save(commit=False)
            lecon.part = chapitre
            lecon.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Ajout"
            action.nom = "A ajouté le chapitre <strong>" + lecon.name + "</strong> pour le cours <strong>" +lecon.part.course.name+ "</strong>"
            action.save()

            messages.success(request, "La leçon a été ajoutée avec succès.")

            return redirect("dashboard:elearning_infos_cours", id=lecon.part.course.id)


    context['form'] = form
    context['cours'] = cours

    return render(request, 'dashboard/elearning/add/add_lecon.html', context)


def elearning_update_lecon(request, id_lecon):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    lecon = get_object_or_404(Elearning_Chapter, id=id_lecon)

    context = {}

    form = FormElearningLecon(request.POST or None, request.FILES or None, instance=lecon)

    if request.method == "POST":

        if form.is_valid():
            lecon = form.save()
            messages.success(request, "La leçon a été modifiée avec succès.")

            action = Action()
            action.date = timezone.now()
            action.admin = admin_logged(request)
            action.type = "Modification"
            action.nom = "A modifié la leçon <strong>" + lecon.name + "</strong> pour le cours <strong>" +lecon.part.course.name+ "</strong>"
            action.save()

            return redirect("dashboard:elearning_infos_cours", id=lecon.part.course.id)

    context['form'] = form
    context['lecon'] = lecon

    return render(request, 'dashboard/elearning/modification/update_lecon.html', context)


def elearning_delete_lecon(request, id_lecon):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les cours", request=request):
        return redirect("dashboard:index")

    lecon = get_object_or_404(Elearning_Chapter, id=id_lecon)
    course_id = lecon.part.course.id

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé la leçon <strong>" + lecon.name + "</strong> pour le cours <strong>" +lecon.part.course.name+ "</strong>"
    action.save()

    lecon.delete()

    messages.success(request, "La leçon a été supprimé.")

    return redirect("dashboard:elearning_infos_cours", id=course_id)


# Coupons

def elearning_coupons(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les coupons", request=request):
        return redirect("dashboard:index")

    context = {}

    context['coupons'] = Elearning_Coupon.objects.all()

    return render(request, "dashboard/elearning/lists/coupons.html", context)


# Categories ajax
def elearning_delete_coupons(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les coupons", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucun coupon sélectionné.'})
    else:
        for id in ids:
            coupon = Elearning_Coupon.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé le coupon Elearning <strong>" + coupon.value + "</strong>"
            action.save()

            coupon.delete()

        return JsonResponse({'status': 'success', 'message': 'Les coupons sélectionnés ont été supprimés.'})


def elearning_add_coupon(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les coupons", request=request):
        return redirect("dashboard:index")

    context = {}

    form = FormElearningCoupon(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            coupon = form.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Ajout"
            action.nom = "A ajouté le coupon Elearning <strong>" + coupon.value + "</strong> "
            action.save()
            form = FormElearningSubCategory()

        messages.success(request, "Le coupon a été ajouté.")
        return redirect('dashboard:elearning_coupons')

    context['form'] = form

    return render(request, 'dashboard/elearning/add/add_coupon.html', context)


def elearning_delete_coupon(request, id):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les coupons", request=request):
        return redirect("dashboard:index")

    coupon = get_object_or_404(Elearning_Coupon, id=id)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé le  coupon Elearning <strong>" + coupon.value + "</strong>"
    action.save()

    coupon.delete()

    messages.success(request, "Le coupon a été supprimé.")

    return redirect("dashboard:elearning_coupons")


def elearning_update_coupon(request, id):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les coupons", request=request):
        return redirect("dashboard:index")

    coupon = get_object_or_404(Elearning_Coupon, id=id)

    context = {}

    form = FormElearningCoupon(request.POST or None,instance=coupon )

    if request.method == "POST":
        if form.is_valid():
            cat = form.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A modifié le coupon Elearning <strong>" + coupon.value + "</strong> "
            action.save()

        messages.success(request, "Le coupon a été modifié.")

    context['form'] = form
    context['coupon'] = coupon

    return render(request, 'dashboard/elearning/modification/update_coupon.html', context)



# Promotions Sales

def elearning_sales(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les promotions", request=request):
        return redirect("dashboard:index")

    context = {}

    context['promotions'] = Elearning_Sale.objects.all()

    return render(request, "dashboard/elearning/lists/promotions.html", context)


# Categories ajax
def elearning_delete_sales(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les promotions", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune promotion sélectionnée.'})
    else:
        for id in ids:
            promo = Elearning_Sale.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé la promotion Elearning <strong>" + str(promo.percentage) + "</strong> pour le cours <strong>" + promo.course.name + "</strong>"
            action.save()

            promo.delete()

        return JsonResponse({'status': 'success', 'message': 'Les promotions sélectionnées ont été supprimées.'})


def elearning_add_sales(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les promotions", request=request):
        return redirect("dashboard:index")

    context = {}

    form = FormElearningSales(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            promo = form.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Ajout"
            action.nom = "A ajouté la promotion Elearning de <strong>" + str(promo.percentage) + " %</strong> pour le cours <strong>"+promo.course.name+"</strong>"
            action.save()

        messages.success(request, "La promotion a été ajoutée.")
        return redirect('dashboard:elearning_sales')

    context['form'] = form

    return render(request, 'dashboard/elearning/add/add_promotion.html', context)


def elearning_delete_sale(request, id):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les promotions", request=request):
        return redirect("dashboard:index")

    promo = get_object_or_404(Elearning_Sale, id=id)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé le  coupon Elearning de  <strong>" + str(promo.percentage) + " % </strong> pour le cours <strong>"+promo.course.name+"</strong>"
    action.save()

    promo.delete()

    messages.success(request, "La promotion a été supprimée.")

    return redirect("dashboard:elearning_sales")


def elearning_update_sales(request, id):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les promotions", request=request):
        return redirect("dashboard:index")

    promo = get_object_or_404(Elearning_Sale, id=id)

    context = {}

    form = FormElearningSales(request.POST or None,instance=promo )

    if request.method == "POST":
        if form.is_valid():
            promo = form.save()

            admin = admin_logged(request)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Modification"
            action.nom = "A modifié le coupon Elearning de <strong>" + str(promo.percentage) + " % </strong> pour le cours <strong>"+promo.course.name+"</strong>"
            action.save()

        messages.success(request, "La promotion a été modifiée.")

    context['form'] = form
    context['promo'] = promo

    return render(request, 'dashboard/elearning/modification/update_promotion.html', context)


# Commandes

def elearning_orders(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les commandes", request=request):
        return redirect("dashboard:index")

    context = {}

    context['commandes'] = Elearning_Order.objects.all()

    return render(request, "dashboard/elearning/lists/liste_commandes.html", context)


# Categories ajax
def elearning_delete_orders(request):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les commandes", request=request):
        return redirect("dashboard:index")

    admin = admin_logged(request)

    ids = request.GET.getlist('ids[]', None)

    if not ids or ids is None:
        return JsonResponse({'status': 'error', 'message': 'Aucune commande sélectionnée.'})
    else:
        for id in ids:
            order = Elearning_Order.objects.get(id=id)

            action = Action()
            action.date = timezone.now()
            action.admin = admin
            action.type = "Suppression"
            action.nom = "A supprimé la commande Elearning <strong> #" + str(order.id) + " : "+str(order.amount)+ " Dh</strong>"
            action.save()

            order.delete()

        return JsonResponse({'status': 'success', 'message': 'Les commandes sélectionnées ont été supprimées.'})


def elearning_order(request, id):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les commandes", request=request):
        return redirect("dashboard:index")

    context = {}

    order = get_object_or_404(Elearning_Order, id=id)

    context['order'] = order

    return render(request, "dashboard/elearning/infos/order.html", context)


def elearning_delete_order(request, id):
    if not admin_has_permission(groupe="Elearning", permission="Gérer les commandes", request=request):
        return redirect("dashboard:index")

    order = get_object_or_404(Elearning_Order, id=id)

    admin = admin_logged(request)

    action = Action()
    action.date = timezone.now()
    action.admin = admin
    action.type = "Suppression"
    action.nom = "A supprimé la commande Elearning <strong> #" + str(order.id) + " : "+str(order.amount)+ " Dh</strong>"
    action.save()

    order.delete()

    messages.success(request, "La commande a été supprimée.")

    return redirect("dashboard:elearning_orders")


#############################End  Elearning

def test(request):
    return render(request, 'dashboard/testapi.html')
