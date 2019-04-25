import urllib
import json
from datetime import datetime, timedelta
import pytz

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from ao.forms import ImportFile
from ao.models import City, Category, AO, Project, AOUser, Keyword, SubCategory, Company, AOSaves, PSaves, Contact, \
    Review, File, FileProject, ContactMail, Newsletter, Quotation, QuotationLine, TVA, QuotationNbRows
from ao.services import send_email,send_multiple_mails
from SocialNetworkJob import settings
from main_app.SendMailBackend import get_custom_connection
from main_app.models import Profil, Image


from tracking_analyzer.models import Tracker



def index(request):
    cities = City.objects.all().annotate(count=Count('project')).order_by('-count')[:4]
    aos = AO.objects.all().order_by('-creation_date').filter(date_limit__gte=datetime.now())[:5]
    categories = Category.objects.all()[:8]

    context = {
        'cities': cities,
        'categories': categories,
        'aos': aos,
        'created_offer': AO.objects.all().count(),
        'created_projects': Project.objects.all().count(),
        'pro_count': AOUser.objects.all().count(),
        'auto_cities': City.objects.all().order_by('name'),
        'auto_keywords': Keyword.objects.all().order_by('name')
    }

    return render(request, 'ao/index.html', context)


def ao_details(request, id_ao):
    ao = get_object_or_404(AO, id=id_ao)

    Tracker.objects.create_from_request(request, ao, ao._meta.verbose_name)

    tvas = TVA.objects.all()


    utc = pytz.UTC
    date_now = utc.localize(datetime.now())
    if ao.date_limit < date_now:
        return redirect('ao:home')

    ao.add_view()

    status = False
    profile_ = None
    if request.user.is_authenticated:
        profile_ = Profil.objects.filter(user=request.user)
        if profile_.count() > 0:
            profile_ = profile_[0]
        else:
            profile_ = None


    if request.method == 'POST':
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
            form = ImportFile(request.POST, request.FILES)
            if form.is_valid():
                if profile_ is not None:
                    if AOUser.objects.filter(user=profile_).count() > 0:
                        file = form.cleaned_data['upload_cv']
                        number = request.POST.get('number', None)
                        money = request.POST.get('money', None)
                        message = request.POST.get('message', None)
                        company_ = AOUser.objects.get(user=profile_).company
                        contact_ = Contact.objects.create(
                            company=company_,
                            ao=ao,
                            budget=money,
                            days=number,
                            message=message,
                            file=file
                        )
                        contact_.save()



                        send_email(contact_.id, 'appel d\'offre')


                        status = True


    idp = None
    is_company = False
    already = False
    if profile_ is not None:
        idp = profile_.id
        company_ = AOUser.objects.filter(user=profile_)
        if company_.count() > 0:
            company_ = company_[0].company
            is_company = True
            if Contact.objects.filter(company=company_, ao=ao).count() > 0:
                already = True

    ao_company = None
    if AOUser.objects.filter(user=ao.user).count() > 0:
        ao_company = AOUser.objects.filter(user=ao.user)[0].company

    quotations = None
    if profile_ == ao.user:
        quotations = Quotation.objects.all().filter(ao=ao)

    devis_already = False
    if is_company:
        if Quotation.objects.filter(company=company_, ao=ao).count() > 0:
            devis_already = True

    devis_nb_lignes =  QuotationNbRows.get_value()

    context = {
        'ao': ao,
        'profile_id': idp,
        'form': ImportFile(),
        'status': status,
        'already': already,
        'is_company': is_company,
        'ao_company': ao_company,
        'quotation_nb_lignes':devis_nb_lignes,
        'lines_number': range(devis_nb_lignes),
        'quotations': quotations,
        'devis_already': devis_already,
        'tvas':tvas,
    }

    return render(request, 'ao/ao.html', context)


def add_ao(request):
    if not request.user.is_authenticated:
        return redirect('ao:home')

    profile_ = request.user.profil
    categories = Category.objects.all().order_by('name')
    status = True

    if request.method == 'POST':
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
            title = request.POST.get('title', None)
            category_ = request.POST.get('category', None)
            date_limit = request.POST.get('date_limit', None)
            email = request.POST.get('email', None)
            tel = request.POST.get('tel', None)
            days = request.POST.get('days', None)
            content = request.POST.get('content', None)

            if title == '' or category_ == '' or email == '' or tel == '' or content == '':
                return redirect('ao:home')

            if date_limit == '':
                date_limit = datetime.now() + timedelta(days=30)
            if days == '':
                days = None

            category_ = get_object_or_404(Category, id=category_)
            ao = AO.objects.create(
                title=title,
                category=category_,
                date_limit=date_limit,
                contact_mail=email,
                contact_phone=tel,
                time_limit=days,
                user=profile_,
                description=content
            )
            ao.save()

            files = request.FILES.getlist('files')
            for f in files:
                file_ = File.objects.create(file=f)
                ao.files.add(file_)
                ao.save()

            return redirect('ao:add_project', ao.id)

        else:
            status = False

    company_ = None
    if AOUser.objects.filter(user=profile_).count() > 0:
        company_ = AOUser.objects.get(user=profile_).company

    context = {
        'profile': profile_,
        'categories': categories,
        'status': status,
        'company': company_
    }

    return render(request, 'ao/add_ao.html', context)


def add_project(request, id_ao):
    ao = get_object_or_404(AO, id=id_ao)

    if not request.user.is_authenticated or request.user.profil != ao.user:
        return redirect('ao:ao', id_ao)

    user = get_object_or_404(Profil, id=ao.user.id)
    categories = SubCategory.objects.all().filter(category=ao.category).order_by('name')
    cities = City.objects.all().order_by('name')
    status = False
    recaptcha = False

    if request.method == 'POST':
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
            title = request.POST.get('title', None)
            budget = request.POST.get('budget', None)
            keywords = request.POST.get('keywords', None)
            description = request.POST.get('content', None)

            project = Project.objects.create(
                ao=ao,
                title=title,
                budget=budget,
                description=description
            )
            project.save()

            cities = request.POST.getlist('city')
            for c in cities:
                c = get_object_or_404(City, id=c)
                project.city.add(c)
                project.save()

            subcategory = request.POST.getlist('subcategory')
            for c in subcategory:
                c = get_object_or_404(SubCategory, id=c)
                project.categories.add(c)
                project.save()

            files = request.FILES.getlist('files')
            for f in files:
                file_ = FileProject.objects.create(file=f)
                project.files.add(file_)
                project.save()

            if keywords is not None:
                keywords = keywords.split(',')
                for k in keywords:
                    if k != '':
                        kw = Keyword.objects.filter(name=k)
                        if kw.count() == 0:
                            kw = Keyword.objects.create(name=k)
                        else:
                            kw = kw[0]
                        project.keywords.add(kw)
                        project.save()

            status = True
        else:
            recaptcha = True

    company_ = None
    if AOUser.objects.filter(user=user).count() > 0:
        company_ = AOUser.objects.get(user=user).company

    context = {
        'ao': ao,
        'profile': user,
        'categories': categories,
        'cities': cities,
        'status': status,
        'recaptcha': recaptcha,
        'company': company_
    }

    return render(request, 'ao/add_project.html', context)


def search(request):

    post = False
    result = AO.objects.all().order_by('-creation_date').filter(date_limit__gte=datetime.now())

    if request.method == 'POST':
        post = True
        city_ = request.POST.get("city", None)
        pro = request.POST.get("pro", None)
        par = request.POST.get("par", None)
        title = request.POST.get("title", None)
        budget = request.POST.get("budget", None)
        date_limit = request.POST.get("dateLimit", None)

        if title is not None and title != '':
            result = result.filter(title__contains=title)

        if city_ is not None and city_ is not '':
            result = result.filter(project__city__name__contains=city_)

        if date_limit is not None and date_limit is not '':
            result = result.filter(date_limit__lte=date_limit)

        category_ = request.POST.getlist("category", None)
        category_count = 0
        for _ in category_:
            category_count += 1
        if category_ is not None and category_count != 0:
            result = result.filter(category__id__in=category_)

        # if project == "on":
        #    result = Project.objects.all().order_by('-creation_date')

        if pro is not None or par is not None:
            if pro == 'on' and par is None:
                result = result.filter(user__id__in=AOUser.user_ids())
            if par == 'on' and pro is None:
                result = result.filter(user__id__in=AOUser.user_ids_not())

        result = list(set(result))
        order = None

        list_budget = []
        if budget is not None and budget != '':
            for ao in result:
                if ao.budget() <= budget:
                    list_budget.append(ao)
            result = list_budget

    else:
        order = request.GET.get('order', 1)
        if order == '1':
            result = result.order_by('-creation_date')
        elif order == '2':
            result = result.order_by('-date_limit')
        elif order == '3':
            result = result.order_by('-views')

    count = 0
    for _ in result:
        count += 1

    if not post:
        # PAGINATOR
        page = request.GET.get('page', 1)
        paginator = Paginator(result, 10)
        try:
            result = paginator.page(page)
        except PageNotAnInteger:
            result = paginator.page(1)
        except EmptyPage:
            result = paginator.page(paginator.num_pages)

    profile_id = None
    if request.user.is_authenticated:
        profile_id = request.user.profil.id

    context = {
        'aos': result,
        'count': count,
        'cities': City.objects.all().values_list('name', flat=True),
        'categories': Category.objects.all().order_by('name'),
        'post': post,
        'order': order,
        'profile_id': profile_id
    }

    return render(request, 'ao/search.html', context)


def project_details(request, id_ao, project_id):
    ao = get_object_or_404(AO, id=id_ao)
    project = get_object_or_404(Project, id=project_id)

    Tracker.objects.create_from_request(request, project, project._meta.verbose_name)

    utc = pytz.UTC
    date_now = utc.localize(datetime.now())
    if ao.date_limit < date_now:
        return redirect('ao:home')

    project.add_view()

    status = False
    profile_ = None
    if request.user.is_authenticated:
        profile_ = Profil.objects.filter(user=request.user)
        if profile_.count() > 0:
            profile_ = profile_[0]
        else:
            profile_ = None

    if request.method == 'POST':
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
            form = ImportFile(request.POST, request.FILES)
            if form.is_valid():
                if profile_ is not None:
                    if AOUser.objects.filter(user=profile_).count() > 0:
                        file = form.cleaned_data['upload_cv']
                        days = request.POST.get('days', None)
                        budget = request.POST.get('budget', None)
                        message = request.POST.get('message', None)
                        company_ = AOUser.objects.get(user=profile_).company
                        contact_ = Contact.objects.create(
                            company=company_,
                            project=project,
                            budget=budget,
                            days=days,
                            message=message,
                            file=file
                        )
                        contact_.save()

                        connection = get_custom_connection()  # Use default email connection

                        # Manually open the connection
                        connection.open()

                        send_email(contact_.id, 'projet')

                        connection.close()

                        status = True

    idp = None
    is_company = False
    already = False
    if profile_ is not None:
        idp = profile_.id
        company_ = AOUser.objects.filter(user=profile_)
        if company_.count() > 0:
            company_ = company_[0].company
            is_company = True
            if Contact.objects.filter(company=company_, project=project).count() > 0:
                already = True

    ao_company = None
    if AOUser.objects.filter(user=project.ao.user).count() > 0:
        ao_company = AOUser.objects.filter(user=project.ao.user)[0].company

    context = {
        'project': project,
        'form': ImportFile(),
        'profile_id': idp,
        'status': status,
        'already': already,
        'is_company': is_company,
        'ao_company': ao_company
    }

    return render(request, 'ao/project.html', context)


def category(request, category_id):
    cat = get_object_or_404(Category, id=category_id)
    cat.add_view()
    aos = AO.objects.filter(category=cat).order_by('-creation_date').filter(date_limit__gte=datetime.now())
    count = aos.count()

    order = request.GET.get('order', 1)
    if order == '1':
        aos = aos.order_by('-creation_date')
    elif order == '2':
        aos = aos.order_by('-date_limit')
    elif order == '3':
        aos = aos.order_by('-views')

    # PAGINATOR
    page = request.GET.get('page', 1)
    paginator = Paginator(aos, 12)
    try:
        aos = paginator.page(page)
    except PageNotAnInteger:
        aos = paginator.page(1)
    except EmptyPage:
        aos = paginator.page(paginator.num_pages)

    profile_id = None
    if request.user.is_authenticated:
        profile_id = request.user.profil.id

    context = {
        'category': cat,
        'aos': aos,
        'count': count,
        'order': order,
        'profile_id': profile_id
    }

    return render(request, 'ao/category.html', context)


def sub_category(request, cat_name, sub_category_id):

    cat = get_object_or_404(Category, name=cat_name)
    sub_cat = get_object_or_404(SubCategory, id=sub_category_id, category=cat)
    sub_cat.add_view()
    projects = sub_cat.project_set.all().order_by('-creation_date').filter(ao__date_limit__gte=datetime.now())
    count = projects.count()

    order = request.GET.get('order', 1)
    if order == '1':
        projects.order_by('-creation_date')
    elif order == '2':
        projects.order_by('-views')
    elif order == '3':
        projects.order_by('-budget')

    # PAGINATOR
    page = request.GET.get('page', 1)
    paginator = Paginator(projects, 12)
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)

    profile_id = None
    if request.user.is_authenticated:
        profile_id = request.user.profil.id

    context = {
        'sub_category': sub_cat,
        'projects': projects,
        'count': count,
        'order': order,
        'profile_id': profile_id
    }

    return render(request, 'ao/sub-category.html', context)


def company(request, company_id):

    comp = get_object_or_404(Company, id=company_id)
    status = False
    connected = False
    if request.user.is_authenticated:
        connected = True

    if connected:
        if request.method == 'POST':
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
                name = request.POST.get('name')
                if name is None or name == '':
                    name = 'anonyme'
                title = request.POST.get('title')
                message = request.POST.get('message')
                user = request.user.profil

                review = Review.objects.create(
                    full_name=name,
                    title=title,
                    content=message,
                    company=comp,
                    user=user
                )
                review.save()
                status = True

    context = {
        'company': comp,
        'connected': connected,
        'status': status
    }
    return render(request, 'ao/company.html', context)


def profile(request, profile_id):
    profile_ = get_object_or_404(Profil, id=profile_id)
    company_ = None
    if AOUser.objects.filter(user=profile_).count() > 0:
        company_ = AOUser.objects.get(user=profile_).company

    aos = profile_.ao_set.filter(date_limit__gte=datetime.now()).order_by('-creation_date')
    # PAGINATOR
    page = request.GET.get('page', 1)
    paginator = Paginator(aos, 10)
    try:
        aos = paginator.page(page)
    except PageNotAnInteger:
        aos = paginator.page(1)
    except EmptyPage:
        aos = paginator.page(paginator.num_pages)

    context = {
        'profile': profile_,
        'aos': aos,
        'company': company_
    }
    return render(request, 'ao/profile.html', context)


def saves(request, profile_id):
    profile_ = get_object_or_404(Profil, id=profile_id)

    if request.user.is_authenticated:
        if request.user != profile_.user:
            return redirect('ao:profile', profile_id)
    else:
        return redirect('ao:profile', profile_id)

    ao_saves = AOSaves.objects.filter(user=profile_).filter(ao__date_limit__gte=datetime.now())\
        .order_by('-creation_date')
    p_saves = PSaves.objects.filter(user=profile_).filter(project__ao__date_limit__gte=datetime.now())\
        .order_by('-creation_date')

    company_ = None
    if AOUser.objects.filter(user=profile_).count() > 0:
        company_ = AOUser.objects.get(user=profile_).company

    context = {
        'aos': ao_saves,
        'projects': p_saves,
        'profile': profile_,
        'company': company_
    }

    return render(request, 'ao/saves.html', context)


def delete_save(request, profile_id, save_id):

    profile_ = get_object_or_404(Profil, id=profile_id)
    if request.user.is_authenticated:
        if request.user != profile_.user:
            return redirect('ao:profile', profile_id)
    else:
        return redirect('ao:profile', profile_id)

    type_ = request.GET.get('type', None)
    if type_ is None:
        return redirect('ao:profile', profile_id)

    if type_ == 'ao':
        s = AOSaves.objects.get(id=save_id)
        if s.user == profile_:
            s.delete()
    elif type_ == 'project':
        s = PSaves.objects.get(id=save_id)
        if s.user == profile_:
            s.delete()
    return redirect('ao:saves', profile_id)


def add_save(request, profile_id, id):

    profile_ = get_object_or_404(Profil, id=profile_id)
    if request.user.is_authenticated:
        if request.user == profile_.user:
            type_ = request.GET.get('type', None)
            if type_ == 'ao':
                ao = get_object_or_404(AO, id=id)
                if AOSaves.objects.filter(user=profile_, ao=ao).count() == 0:
                    AOSaves.objects.create(user=profile_, ao=ao).save()
                data = {'status': True}
            elif type_ == 'project':
                project = get_object_or_404(Project, id=id)
                if PSaves.objects.filter(user=profile_, project=project).count() == 0:
                    PSaves.objects.create(user=profile_, project=project).save()
                data = {'status': True}
            else:
                data = {'status': False}
            return JsonResponse(data)
    return JsonResponse({'status': False})


def contacted(request, profile_id):
    profile_ = get_object_or_404(Profil, id=profile_id)
    if request.user.is_authenticated:
        if request.user != profile_.user:
            return redirect('ao:profile', profile_id)
    else:
        return redirect('ao:profile', profile_id)

    if AOUser.objects.filter(user=profile_).count() == 0:
        return redirect('ao:profile', profile_id)

    company_ = AOUser.objects.get(user=profile_).company
    ao_contacted = Contact.objects.filter(company=company_, ao__isnull=False, active=True).order_by('-creation_date')\
        .filter(ao__date_limit__gte=datetime.now())
    p_contacted = Contact.objects.filter(company=company_, project__isnull=False, active=True)\
        .order_by('-creation_date').filter(project__ao__date_limit__gte=datetime.now())

    context = {
        'profile_id': profile_id,
        'aos': ao_contacted,
        'projects': p_contacted,
        'company': AOUser.objects.get(user=profile_).company
    }

    return render(request, 'ao/contacted.html', context)


def delete_contacted(request, profile_id, contacted_id):

    company_ = get_object_or_404(Company, id=profile_id)
    profile_ = get_object_or_404(AOUser, company=company_).user
    if request.user.is_authenticated:
        if request.user != profile_.user:
            return redirect('ao:profile', profile_id)
    else:
        return redirect('ao:profile', profile_id)

    contact = Contact.objects.get(id=contacted_id)
    if contact.company == AOUser.objects.get(user=profile_).company:
        contact.active = False
        contact.save()

    return redirect('ao:contacted', profile_id)


def delete_ao(request, ao_id):
    ao = get_object_or_404(AO, id=ao_id)
    if request.user.is_authenticated:
        if request.user.profil == ao.user:
            ao.delete()
            return redirect('ao:profile', ao.user.id)
    return redirect('ao:ao', ao_id)


def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user.is_authenticated:
        if request.user.profil == project.ao.user:
            project.delete()
            return redirect('ao:ao', project.ao.id)
    return redirect('ao:project', project_id)


def edit_ao(request, ao_id):
    if not request.user.is_authenticated:
        return redirect('ao:home')

    ao = get_object_or_404(AO, id=ao_id)

    profile_ = request.user.profil
    if ao.user != profile_:
        return redirect('ao:ao', ao_id)

    categories = Category.objects.all().order_by('name')
    status = True

    if request.method == 'POST':
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
            title = request.POST.get('title', None)
            category_ = request.POST.get('category', None)
            date_limit = request.POST.get('date_limit', None)
            email = request.POST.get('email', None)
            tel = request.POST.get('tel', None)
            days = request.POST.get('days', None)
            content = request.POST.get('content', None)

            if title == '' or category_ == '' or email == '' or tel == '' or content == '':
                return redirect('ao:home')

            if date_limit == '':
                date_limit = datetime.now() + timedelta(days=30)
            if days == '':
                days = None

            category_ = get_object_or_404(Category, id=category_)
            if ao.project_set.count() == 0:
                ao.category = category_

            ao.title = title
            ao.date_limit = date_limit
            ao.contact_mail = email
            ao.contact_phone = tel
            ao.time_limit = days
            ao.description = content
            ao.save()

            if ao.get_interested_mails():
                sujet = "Un changement a été effectué à l'appel d'offre qui vous interesse"

                connection = get_custom_connection()  # Use default email connection

                # Manually open the connection
                connection.open()

                send_multiple_mails(emails_addresses=ao.get_interested_mails(),sujet=sujet,message=sujet,request=request,object_=ao,type_='ao',company=None)

                connection.close()

            files = request.FILES.getlist('files')
            if len(files) == 0 and ao.files.all().count() > 0:
                return redirect('ao:ao', ao.id)

            for file in ao.files.all():
                file.delete()

            for f in files:
                file_ = File.objects.create(file=f)
                ao.files.add(file_)
                ao.save()

            return redirect('ao:ao', ao.id)

        else:
            status = False

    company_ = None
    if AOUser.objects.filter(user=profile_).count() > 0:
        company_ = AOUser.objects.get(user=profile_).company

    context = {
        'ao': ao,
        'profile': profile_,
        'categories': categories,
        'status': status,
        'company': company_
    }

    return render(request, 'ao/edit_ao.html', context)


def edit_project(request, id_ao, id_project):
    ao = get_object_or_404(AO, id=id_ao)
    project = get_object_or_404(Project, id=id_project)

    if not request.user.is_authenticated or request.user.profil != ao.user:
        return redirect('ao:ao', id_ao)

    user = get_object_or_404(Profil, id=ao.user.id)
    categories = SubCategory.objects.all().filter(category=ao.category).order_by('name')
    cities = City.objects.all().order_by('name')
    status = False
    recaptcha = False

    if request.method == 'POST':
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
            title = request.POST.get('title', None)
            budget = request.POST.get('budget', None)
            keywords = request.POST.get('keywords', None)
            description = request.POST.get('content', None)

            if title == '' or budget == '' or description == '':
                return redirect('ao:home')

            project.title = title
            if ',' in budget:
                budget = budget.split(',')[0]
            project.budget = budget
            project.description = description
            project.save()

            cities = request.POST.getlist('city')
            if project.city.all().count() > 0:
                project.city.clear()
            for c in cities:
                c = get_object_or_404(City, id=c)
                project.city.add(c)
                project.save()

            subcategory = request.POST.getlist('subcategory')
            if project.categories.all().count() > 0:
                project.categories.clear()
            for c in subcategory:
                c = get_object_or_404(SubCategory, id=c)
                project.categories.add(c)
                project.save()

            files = request.FILES.getlist('files')
            for f in files:
                file_ = FileProject.objects.create(file=f)
                project.files.add(file_)
                project.save()

            if keywords is not None:
                project.keywords.clear()
                keywords = keywords.split(',')
                for k in keywords:
                    if k != '':
                        kw = Keyword.objects.filter(name=k)
                        if kw.count() == 0:
                            kw = Keyword.objects.create(name=k)
                        else:
                            kw = kw[0]
                        project.keywords.add(kw)
                        project.save()


            if project.get_interested_mails():
                sujet = "Un changement a été effectué à l'appel d'offre qui vous interesse"

                connection = get_custom_connection()  # Use default email connection

                # Manually open the connection
                connection.open()

                send_multiple_mails(emails_addresses=project.get_interested_mails(),sujet=sujet,message=sujet,request=request,object_=project,type_='lot',company=None)

                connection.close()

            status = True
            return redirect('ao:project', id_ao, id_project)
        else:
            recaptcha = True

    company_ = None
    if AOUser.objects.filter(user=user).count() > 0:
        company_ = AOUser.objects.get(user=user).company

    context = {
        'project': project,
        'ao': ao,
        'profile': user,
        'categories': categories,
        'cities': cities,
        'status': status,
        'recaptcha': recaptcha,
        'company': company_
    }

    return render(request, 'ao/edit_project.html', context)


def update_date(request, ao_id):
    if not request.user.is_authenticated:
        return redirect('ao:home')

    ao = get_object_or_404(AO, id=ao_id)

    profile_ = request.user.profil
    if ao.user != profile_:
        return redirect('ao:ao', ao_id)

    if request.method == 'POST':
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
            new_date = request.POST.get('date_limit', None)
            if new_date != '' and new_date is not None:
                ao.date_limit = new_date
                ao.save()

    return redirect('ao:ao', ao_id)


def city(request, city_id):

    city_ = get_object_or_404(City, id=city_id)
    ids = []
    for ao in city_.aos():
        ids.append(ao.id)

    aos = AO.objects.all().filter(id__in=ids, date_limit__gte=datetime.now())

    order = request.GET.get('order', 1)
    if order == '1':
        aos = aos.order_by('-creation_date')
    elif order == '2':
        aos = aos.order_by('-date_limit')
    elif order == '3':
        aos = aos.order_by('-views')

    # PAGINATOR
    page = request.GET.get('page', 1)
    paginator = Paginator(aos, 5)
    try:
        aos = paginator.page(page)
    except PageNotAnInteger:
        aos = paginator.page(1)
    except EmptyPage:
        aos = paginator.page(paginator.num_pages)

    profile_id = None
    if request.user.is_authenticated:
        profile_id = request.user.profil.id

    context = {
        'aos': aos,
        'city': city_,
        'order': order,
        'profile_id': profile_id
    }

    return render(request, 'ao/city.html', context)


def contact(request):

    status = False
    recaptcha = False
    if request.method == 'POST':
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
            name = request.POST.get('name', None)
            email = request.POST.get('email', None)
            subject = request.POST.get('subject', None)
            message = request.POST.get('message', None)

            if name == '' or email == '' or subject == '' or message == '':
                return redirect('ao:home')

            contact_ = ContactMail.objects.create(
                full_name=name,
                email=email,
                subject=subject,
                message=message
            )
            contact_.save()
            status = True

        else:
            recaptcha = True

    context = {
        'status': status,
        'recaptcha': recaptcha
    }

    return render(request, 'ao/contact.html', context)


def add_newsletter(request):
    if request.method == 'POST':
        status = True
        email = request.POST.get('email', None)
        if email is None or email == '':
            status = False
        else:
            if Newsletter.objects.filter(email=email).count() == 0:
                Newsletter.objects.create(
                    email=email
                )
    else:
        status = False

    return JsonResponse({'status': status})


def profile_settings(request):

    if not request.user.is_authenticated:
        return redirect('ao:home')
    profile_ = request.user.profil
    profile_ = Profil.objects.get(id=profile_.id)

    company_ = None
    if AOUser.objects.filter(user=profile_).count() > 0:
        company_ = AOUser.objects.get(user=profile_).company

    status = None
    if request.method == 'POST':
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
            image = request.FILES.get('image', None)
            first_name = request.POST.get('name', None)
            last_name = request.POST.get('lastname', None)
            function_p = request.POST.get('function', None)
            phone = request.POST.get('phone', None)
            fax = request.POST.get('fax', None)
            resume = request.POST.get('resume', None)

            if first_name is None or last_name is None or function_p is None or phone is None or fax is None:
                return redirect('ao:profile', profile_.id)

            profile_.user.first_name = first_name
            profile_.user.last_name = last_name
            profile_.user.save()
            profile_.fonction = function_p
            profile_.tel_portable = phone
            profile_.tel_fixe = fax
            profile_.resume = resume
            if image is not None:
                image_c = Image.objects.create(image=image)
                profile_.photo_profil = image_c
            profile_.save()

            if company_ is not None:
                # Company fields
                image_e = request.FILES.get('image_e', None)
                name_e = request.POST.get('name_e', None)
                activity_e = request.POST.get('activity', None)
                city_e = request.POST.get('city_e', None)
                code_e = request.POST.get('code_e', None)
                address_e = request.POST.get('address_e', None)
                desc_e = request.POST.get('desc_e', None)
                email_e = request.POST.get('email_e', None)
                tel_e = request.POST.get('tel_e', None)
                fax_e = request.POST.get('fax_e', None)
                trade_registry_e = request.POST.get('rc_e', None)
                fb_e = request.POST.get('fb_e', None)
                twitter_e = request.POST.get('twitter_e', None)
                youtube_e = request.POST.get('youtube_e', None)
                linkedin_e = request.POST.get('linkedin_e', None)
                github_e = request.POST.get('github_e', None)

                if image_e is not None:
                    company_.logo = image_e
                company_.name = name_e
                company_.activity = activity_e
                company_.city = city_e
                company_.codePostal = code_e
                company_.address = address_e
                company_.description = desc_e
                company_.mail = email_e
                company_.telephone = tel_e
                company_.fax = fax_e
                company_.trade_registry = trade_registry_e
                company_.facebook = fb_e
                company_.twitter = twitter_e
                company_.youtube = youtube_e
                company_.linkedIn = linkedin_e
                company_.github = github_e
                company_.save()

            status = True
        else:
            status = False

    functions = {
        'Agent de service public',
        'Architecte',
        'Artisan',
        'Chef de projet',
        'Commerçant',
        'Consultant',
        'Directeur - Chef de service',
        'Direction générale(PDG, DG, Gérant)',
        'Elu local, Conseiller municipaux',
        'Elu territorial, Conseiller Général / Conseil Régional',
        'Enseignant chercheur',
        'Etudiant',
        'Haut fonctionnaire(Etat / Ministères)',
        'Ingénieur',
        'Président, Vice - Président',
        'Responsable - Chargé - Attaché',
        'Technicien',
        'Urbaniste - Paysagiste',
        'Autre'
    }

    context = {
        'profile': profile_,
        'company': company_,
        'functions': functions,
        'status': status
    }

    return render(request, 'ao/profile_settings.html', context)


def be_company(request):
    if not request.user.is_authenticated:
        return redirect('ao:home')
    profile_ = request.user.profil

    company_ = None
    if AOUser.objects.filter(user=profile_).count() > 0:
        company_ = AOUser.objects.get(user=profile_).company

    if company_ is not None:
        return redirect('ao:company', profile_.id)

    status = False
    if request.method == 'POST':
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
            logo = request.FILES.get('logo', None)
            name = request.POST.get('name_e', None)
            activity = request.POST.get('activity', None)
            city_ = request.POST.get('city_e', None)
            cp = request.POST.get('code_e', None)
            address = request.POST.get('address_e', None)
            description = request.POST.get('description', None)
            email = request.POST.get('email_e', None)
            phone = request.POST.get('tel_e', None)
            fax = request.POST.get('fax_e', None)
            trade_registry = request.POST.get('rc_e', None)
            fb = request.POST.get('fb_e', None)
            twitter = request.POST.get('twitter_e', None)
            youtube = request.POST.get('youtube_e', None)
            linked = request.POST.get('linkedin_e', None)
            github = request.POST.get('github_e', None)

            company_user = Company.objects.create(
                name=name,
                activity=activity,
                address=address,
                city=city_,
                codePostal=cp,
                telephone=phone,
                fax=fax,
                mail=email,
                trade_registry=trade_registry,
                logo=logo,
                description=description,
                facebook=fb,
                twitter=twitter,
                youtube=youtube,
                linkedIn=linked,
                github=github
            )
            company_user.save()
            AOUser.objects.create(
                user=profile_,
                company=company_user
            )
            return redirect('ao:profile_settings')
        else:
            status = True

    context = {
        'profile': profile_,
        'status': status
    }
    return render(request, 'ao/create_company.html', context)


@require_POST
def send_quotation(request, ao_id):
    if not request.user.is_authenticated:
        return redirect('ao:home')
    profile_ = request.user.profil

    company_ = None
    if AOUser.objects.filter(user=profile_).count() > 0:
        company_ = AOUser.objects.get(user=profile_).company

    if company_ is None:
        return redirect('ao:ao', ao_id)

    ao = get_object_or_404(AO, id=ao_id)

    days = request.POST.get("numberD", None)
    money = request.POST.get("moneyD", None)
    message = request.POST.get("message", None)
    tva = request.POST.get("tva", None)

    quotation = Quotation.objects.create(
        ao=ao,
        company=company_,
        days=days,
        budget=money,
        message=message,
        tva=tva
    )
    quotation.save()

    numbers = '0123456789'
    for n in numbers:
        price = request.POST.get("price"+n, None)
        # price_number = request.POST.get("np"+n, None)
        design = request.POST.get("design"+n, None)
        unite = request.POST.get("unite"+n, None)
        qte = request.POST.get("qte"+n, None)
        if price is not None and price != '' and design is not None and design != '' and unite is not None \
                and unite != '' and qte is not None and qte != '': #and price_number is not None and price_number != ''
            QuotationLine.objects.create(
                quotation=quotation,
                # price_number=price_number,
                designation=design,
                unit=unite,
                qte=qte,
                price=price
            )
    return redirect('ao:ao', ao_id)


def devis_details(request, ao_id, devis_id):
    ao = get_object_or_404(AO, id=ao_id)
    devis = get_object_or_404(Quotation, id=devis_id)

    if not request.user.is_authenticated:
        print(1)
        return redirect('ao:ao', ao_id)
    profile_ = request.user.profil

    if ao.user != profile_:
        return redirect('ao:ao', ao_id)

    devis_lines = devis.quotationline_set.all()

    context = {
        'devis': devis,
        'devis_lines': devis_lines,
    }

    return render(request, 'ao/devis_info.html', context)

#Chipop

#AO : Add users who downloaded documents

def ao_download_document(request,id):
    ao = get_object_or_404(AO,id=id)

    if request.user.is_authenticated:
        profile_ = Profil.objects.filter(user=request.user)
        if profile_.count() > 0:
            profile_ = profile_[0]
        else:
            profile_ = None


    if AOUser.objects.filter(user=profile_).count() > 0:
        #C'est une entreprise
        aouser = AOUser.objects.filter(user=profile_)[0]
        if profile_ is not aouser.user:
            ao.downloaded_piecejointe_companies.add(aouser.company)
    else:
        #C'est un particulier
        ao.downloaded_piecejointe_users.add(profile_)
    return HttpResponse('done')


def project_download_document(request,id):
    lot = get_object_or_404(Project,id=id)

    if request.user.is_authenticated:
        profile_ = Profil.objects.filter(user=request.user)
        if profile_.count() > 0:
            profile_ = profile_[0]
        else:
            profile_ = None

    if AOUser.objects.filter(user=profile_).count() > 0:
        #C'est une entreprise
        aouser = AOUser.objects.filter(user=profile_)[0]
        if profile_ is not aouser.user:
            lot.downloaded_piecejointe_companies.add(aouser.company)
    else:
        #C'est un particulier
        lot.downloaded_piecejointe_users.add(profile_)

    return HttpResponse('done')