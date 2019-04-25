from django.core.mail import send_mail
from django.shortcuts import render, redirect, resolve_url
from django.http import HttpResponse, Http404, HttpResponseRedirect
from .models import *
from .forms import *
from .SendMailBackend import get_custom_connection

from django.template.loader import get_template
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.urls import reverse
from django.utils.timezone import now
from django.contrib.auth.tokens import default_token_generator
from django.template.response import TemplateResponse
from django.db.models import Max
from journal.models import News,Journalist,Image as Journalist_Image

import json
import urllib
from django.conf import settings

from dashboard.models import Parameters


from pusher_chat_app.utils import pusher_create_user

# Create your views here.


def home(request):
    context = dict()
    context['contact_form'] = ContactForm()
    context['last_articles'] = News.objects.filter(active=True, approved=True).order_by('-date_publication')[:6]
    context['is_home'] = True
    context['parameters'] = Parameters.get_object()

    newsletter = request.GET.get('newsletter',None)
    if newsletter == 1:
        context['newsletter_message'] = True
        print(context['newsletter_message'])

    return render(request, 'index1.html', context)


def newsletter_subscribe(request):
    context = dict()
    context['contact_form'] = ContactForm()
    context['last_articles'] = News.objects.filter(active=True, approved=True).order_by('-date_publication')[:6]

    if request.method == "POST":
        email = request.POST.get('newsletter_email',None)
        if email is not None:
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            ''' End reCAPTCHA validation '''

            if result['success']:
                newsletter = NewsLetterMails(email = email)
                newsletter.save()
                messages.success(request,"Votre inscription a bien été effectuée.")
                print('inscription réussie')

            else:
                print("captcha error")
                messages.error(request, "Le reCaptcha est invalide. Merci de réessayer.")

            return redirect(resolve_url('main_app:home') + '?newsletter=1#newsletter')

    return redirect(resolve_url('main_app:home') + '?newsletter=1#newsletter')


def test(request):
    return render(request, 'index.html')


def signup(request):
    if request.user.is_authenticated:
        messages.info(request, "Vous êtes connecté")
        return redirect('main_app:home')
    if request.method == 'POST':




        conditions = request.POST.get('conditions')
        form_profil_inscription = FormProfilInscription(request.POST)
        form_user_inscription = FormUserInscription(request.POST)
        
        if conditions is None:
            messages.error(request, "Vous n'avez pas accepté nos termes générales d'utilisations.")
            context = dict()
            context['contact_form'] = ContactForm()
            context['last_articles'] = News.objects.filter(active=True, approved=True).order_by('-date_publication')[:6]
            context['form_profil_inscription'] = form_profil_inscription
            context['form_user_inscription'] = form_user_inscription

            return render(request, 'authentification/signupNew.html', context)

        if form_profil_inscription.is_valid() and form_user_inscription.is_valid():
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            ''' End reCAPTCHA validation '''

            if result['success']:
                userr = form_user_inscription.save(commit=False)
                nb = User.objects.all().aggregate(Max('id'))['id__max']
                if nb is None:
                    nb = 0
                username = nb + 1
                user = User.objects.create_user(username, userr.email, userr.password)
                user.first_name = userr.first_name
                user.last_name = userr.last_name
                user.is_active = False
                user.save()
                profil = form_profil_inscription.save(commit=False)
                profil.civilite = form_profil_inscription.cleaned_data.get('civilite')
                """""""""
                if profil.civilite == 'Mr':
                    photo_profil = Image.objects.get(image="default_profil_m.png")
                else:
                    photo_profil = Image.objects.get(image="default_profil_f.png")
                """""""""

                try:
                    if profil.civilite == 'Mr':
                        photo_profil = Image.objects.get(image="default_profil_m.png")
                    else:
                        photo_profil = Image.objects.get(image="default_profil_f.png")
                except Exception as e:
                    photo_profil = Image()
                    if profil.civilite == 'Mr':
                        photo_profil.image = "/default_profil_m.png"
                    else:
                        photo_profil.image = "/default_profil_f.png"
                    photo_profil.save()

                try:
                    photo_couverture = Image.objects.get(image="default_cover.png")
                except Exception as e:
                    photo_couverture = Image()
                    photo_couverture.image = "/default_cover.png"
                    photo_couverture.save()

                if form_profil_inscription.cleaned_data.get('votre_profile') == "Vous êtes un professionnel" :
                    profil.is_professional = True
                    profil.is_active_professional = False
                if form_profil_inscription.cleaned_data.get('votre_profile') == "Vous êtes un journaliste/éditeur":
                    profil.is_journaliste = True
                    profil.is_active_professional = False
                    j = Journalist()
                    j.last_name = user.last_name
                    j.first_name = user.first_name
                    j.email = user.email
                    tel  = ""
                    if profil.tel:
                        tel = profil.tel[29:]
                    j.tel = tel
                    try:
                        img = Journalist_Image.objects.get(image="images/profileImage.jpg")
                    except Exception as e:
                        img = Journalist_Image()
                        img.image  = "images/profileImage.jpg"
                        img.description = "Profile Picture"
                        img.save()

                    j.profile_picture = img
                    j.save()

                    j.save()
                if form_profil_inscription.cleaned_data.get('votre_profile') == "Vous êtes un étudiant":
                    profil.is_etudiant = True
                if form_profil_inscription.cleaned_data.get('votre_profile') == "Vous êtes un particulier":
                    profil.is_particulier = True

                profil.photo_profil = photo_profil
                profil.photo_couverture = photo_couverture
                profil.user = user
                profil.save()
                pusher_create_user(request,profil.user.id,profil.user.get_full_name())

                send_confirmation_signup_mail(request, user)  # une méthode qu'on a nous meme défini ( un peu plus bas )
                context = dict()
                context['contact_form'] = ContactForm()
                context['last_articles'] = News.objects.filter(active=True, approved=True).order_by(
                    '-date_publication')[:6]
                context['form_profil_inscription'] = form_profil_inscription
                context['form_user_inscription'] = form_user_inscription

                return redirect('main_app:signup_complete')
            else:
                messages.error(request, "Le reCaptcha est invalide. Merci de réessayer.")
        else:
            context = dict()
            context['contact_form'] = ContactForm()
            context['last_articles'] = News.objects.filter(active=True, approved=True).order_by('-date_publication')[:6]
            context['form_profil_inscription'] = form_profil_inscription
            context['form_user_inscription'] = form_user_inscription

            return render(request, 'authentification/signupNew.html', context)
    else:
        form_profil_inscription = FormProfilInscription()
        form_user_inscription = FormUserInscription()

    context = dict()
    context['contact_form'] = ContactForm()
    context['last_articles'] = News.objects.filter(active=True, approved=True).order_by('-date_publication')[:6]
    context['form_profil_inscription'] = form_profil_inscription
    context['form_user_inscription'] = form_user_inscription

    return render(request, 'authentification/signupNew.html', context)


def signup_complete(request):


    #if not messages:
    #   raise Http404('Bonjour')

    context = dict()
    context['contact_form'] = ContactForm()
    context['last_articles'] = News.objects.filter(active=True, approved=True).order_by('-date_publication')[:6]

    return render(request, 'authentification/signup_thankyou.html',context)


def confirm_email_signup(request, id_user, token_email):
    user = get_object_or_404(User, id=id_user)

    if user.is_active:
        messages.warning(request, "Votre email est déjà confirmé.")
        return redirect('main_app:log_in')

    if user.profil.token_email_expiration <= timezone.now():
        messages.warning(request,
                         "Votre lien a expiré. <strong><a href='/main/confirm_mail/resend'>Renvoyer l'email</a></strong> ")
        return redirect('main_app:log_in')
    else:
        if user.profil.token_email == token_email:
            user.is_active = True
            user.save()
            messages.success(request, "Votre email a été confirmé.")
            return redirect('main_app:log_in')
        else:
            raise Http404("Une erreur s'est produite.")

    return redirect('main_app:log_in')


def log_in(request):
    if request.user.is_authenticated:
        return redirect('main_app:home')
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email.lower())  # on le récupère juste pour vérifier s'il est actif
        except:
            user = None

        if user is not None:
            if not user.is_active:
                messages.warning(request,
                                 "Votre compte n'est pas encore activé, Veuiller l'activer en cliquant sur le lien vous a été envoyé via mail. <strong><a href='/confirm_mail/resend/'>Renvoyer l'email</a></strong> ")
                return redirect('main_app:log_in')
            elif (user.profil.is_professional or user.profil.is_journaliste) and not user.profil.is_active_professional :
                messages.warning(request,"L'administration activera votre compte dans les plus bref delais.")
                print("not active")
                return redirect('main_app:log_in')

            else:  # S'il a un email valide + est actif , on verifie son mdp
                print("active")
                user = authenticate(username=email,
                                    password=password)  # ici on le récupère pour voir s'il a tapé le bon mdp
                if user is not None:  # Si l'email valide + password  valide + actif
                    login(request, user)
                    return redirect('main_app:home')
                else:
                    messages.error(request, "L'email ou le mot de passe est incorrect.")
                    return redirect('main_app:log_in')
        else:
            messages.error(request, "L'email ou le mot de passe est incorrect.")
            return redirect('main_app:log_in')

    context = dict()
    context['contact_form'] = ContactForm()
    context['last_articles'] = News.objects.filter(active=True, approved=True).order_by('-date_publication')[:6]
    context['form_login'] = loginform()
    return render(request, "authentification/login_ESPR.html", context)


def password_reset(request, is_admin_site=False, template_name='authentification/reset_password_form_ESPR.html',
                   email_template_name='emails/reset_password_email.html',
                   subject_template_name='authentification/reset_password_subject.txt',
                   password_reset_form=PasswordResetForm, token_generator=default_token_generator,
                   post_reset_redirect=None, from_email=None, current_app=None, extra_context=None,
                   html_email_template_name='emails/reset_password_email.html'):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('main_app:password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                'html_email_template_name': html_email_template_name,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form_reset_password': form,
        'title': ('Password reset'),
    }
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)


def log_out(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('main_app:home')
    else:
        return redirect('main_app:log_in')


def send_confirmation_signup_mail(request,
                                  user=None):  # Methode normal , pas une vue, utilisée pour envoyer un mail dans la view signup et confirm_mail_resend

    if user is None:
        messages.error(request,
                       'Une erreur s\'est produite.<br>Peut être que l\'email indiqué n\'est pas enregistré.<br>Veuillez Réessayer ')
    elif user.is_active:
        messages.warning(request,
                         'Votre compte est déjà activé')

    else:
        generated_token = get_random_string(length=32)
        user.profil.token_email = generated_token
        user.profil.token_email_expiration = timezone.now() + timedelta(days=2)
        user.profil.save()
        message = get_template('emails/signup_confirm_email.html').render({'user': user,'request':request})

        send_mail(
            'ESPR : Finalisez votre inscription',
            message,
            Parameters.get_object().email_host_user,
            [user.email],
            fail_silently=False,
            html_message=message,
            connection=get_custom_connection()
        )

        messages.success(request,
                         'Un e-mail de vérification vous a été envoyé à l\'adresse ' + user.email + '.<br>Cliquez sur le lien inclu dans l\'e-mail pour activer votre compte. ')

        if (user.profil.is_professional or user.profil.is_journaliste) and not user.profil.is_active_professional :
            messages.success(request,"Après verification par email, l'administration activera votre compte dans les plus bref delais.")


def confirm_mail_resend(
        request):  # Vue utilisée quand on clique sur Renvoyer un autre email et qu'on tape l'email dans le formulaire, on le recupere par get
    if 'email' in request.GET:
        try:
            user = User.objects.get(email=request.GET.get('email').lower())
        except:
            user = None

        send_confirmation_signup_mail(request, user)

    return render(request, 'authentification/confirm_mail_form_ESPR.html')


def contactus(request):
    if request.method == 'POST':

        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req = urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            ''' End reCAPTCHA validation '''

            if result['success']:
                contact_form.save(commit=True)
                messages.success(request,
                                 'Votre message a été envoyé.<br>Nous vous répondrons dans les plus bref délais.')
            else:
                messages.error(request,"Le reCaptcha est invalide. Merci de réessayer.")

            if 'is_home' in request.POST:
                return redirect(resolve_url('main_app:home') + '#contact?is_home=1')
            context = dict()
            context['contact_form'] = contact_form
            context['last_articles'] = News.objects.filter(active=True, approved=True).order_by('-date_publication')[:6]
            context['is_home'] = False
            return render(request, 'main/contactus_ESPR.html',context)
        else:
            print("here 3")
            contact_form = ContactForm()
            print(contact_form.errors)

    print("here 2")
    context = dict()
    contact_form = ContactForm()
    context['contact_form'] = contact_form
    context['last_articles'] = News.objects.filter(active=True, approved=True).order_by('-date_publication')[:6]

    return render(request, 'main/contactus_ESPR.html', {'contact_form': contact_form})


def error_400(request):
    return render(request, 'errors_pages/400.html')


def error_403(request):
    return render(request, 'errors_pages/403.html')


def error_404(request):
    return render(request, 'errors_pages/404.html')


def error_500(request):
    return render(request, 'errors_pages/500.html')

