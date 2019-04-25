import urllib
import json
from datetime import datetime

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from itertools import chain

from tracking_analyzer.models import Tracker

from main_app.models import Profil, Image
from qa.forms import AnswerForm, AddQuestionForm, AddPostForm, UpdateProfileForm, UpdatePImageForm, UpdateCImageForm, \
    ContactForm
from qa.models import Question, Tag, Answer, Category, Article, Comment, ContactMessage, Notification, SignalQuestion, \
    SignalAnswer, SignalArticle, SignalComment


from SocialNetworkJob import settings


# QA VIEWS

def index(request):

    latest_questions = Question.objects.all().annotate(answers_count=Count('answer')).order_by("-creation_date")[:9]
    latest_answers = Answer.objects.all().order_by("-creation_date")[:6]
    top_author = Profil.objects.filter(points__gte=0).order_by('-points')[:6]

    tags = {}
    i = 1
    for q in latest_questions:
        tags[i] = Tag.objects.filter(question=q).all()
        i = i + 1

    context = {
        'latest_questions': latest_questions,
        'latest_answers': latest_answers,
        'top_author': top_author,
        'tags': tags
    }

    return render(request, 'qa/index.html', context)


def question_detail(request, qst_id):
    qst = get_object_or_404(Question, id=qst_id)
    Tracker.objects.create_from_request(request, qst, qst._meta.verbose_name)
    qst.add_view()

    count_answer = Answer.objects.filter(user=qst.user).count()

    answers = qst.answer_set.all().order_by('-likes')

    top_questions = Question.objects.all().order_by("-views_number")[:6]
    latest_answers = Answer.objects.all().order_by("-creation_date")[:6]

    answer_form = AnswerForm()

    message = request.session.get('message_answer', None)
    if message is not None:
        del request.session['message_answer']

    owner = False
    user_a_id = None
    if request.user.is_authenticated:
        user_a_id = request.user.profil.id
        if request.user.profil == qst.user:
            owner = True

    context = {
        'question': qst,
        'q_tags': Tag.objects.filter(question=qst),
        'count_answer': count_answer,
        'answers': answers,
        'top_questions': top_questions,
        'latest_answers': latest_answers,
        'answer_form': answer_form,
        'message': message,
        'owner': owner,
        'user_a_id': user_a_id
    }
    return render(request, 'qa/question-detail.html', context)


def category(request, category_id):

    cat = get_object_or_404(Category, id=category_id)

    Tracker.objects.create_from_request(request, cat, cat._meta.verbose_name)

    top_questions = Question.objects.all().order_by("-views_number")[:6]
    latest_answers = Answer.objects.all().order_by("-creation_date")[:6]

    questions = Question.objects.filter(category=cat).annotate(answers_count=Count('answer')).order_by('-creation_date')

    answers_number = 0

    tags = {}
    i = 1
    for q in questions:
        answers_number += q.answer_set.count()
        tags[i] = Tag.objects.filter(question=q).all()
        i = i + 1

    page = request.GET.get('page', 1)
    paginator = Paginator(questions, 7)
    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)

    context = {
        'top_questions': top_questions,
        'latest_answers': latest_answers,
        'category': cat,
        'questions': questions,
        'tags': tags,
        'questions_number': cat.question_set.count(),
        'answers_number': answers_number,
    }

    return render(request, 'qa/category.html', context)


def all_questions(request):

    top_questions = Question.objects.all().order_by("-views_number")[:6]
    latest_answers = Answer.objects.all().order_by("-creation_date")[:6]
    top_author = Profil.objects.filter(points__gte=0).order_by('-points')[:6]
    categories = Category.objects.all().order_by('title')
    all_tags = Tag.objects.all().order_by('title')

    text = None

    tag = request.GET.get('tag', None)
    search = request.GET.get('search', None)
    if search is None:
        search = request.GET.get('q', None)

    if search is not None and search != '':
        questions_a = Question.objects.filter(title__contains=search)\
            .annotate(answers_count=Count('answer')).order_by('-creation_date')
        exclude_list_1 = questions_a.values_list('id', flat=True)
        questions_b = Question.objects.filter(category__title__contains=search).exclude(id__in=exclude_list_1)\
            .annotate(answers_count=Count('answer')).order_by('-creation_date')
        exclude_list_2 = questions_b.values_list('id', flat=True)
        questions_c = Question.objects.filter(tags__title__contains=search).exclude(id__in=exclude_list_1)\
            .exclude(id__in=exclude_list_2).annotate(answers_count=Count('answer')).order_by('-creation_date')

        questions = list(chain(questions_a, questions_b, questions_c))

        questions_number = questions_a.count() + questions_b.count() + questions_c.count()
        text = 'Résultat de recherche sur <strong>' + search + '</strong> '

    elif tag is not None:
        tag = get_object_or_404(Tag, title=tag)
        questions = tag.question_set.annotate(answers_count=Count('answer')).order_by('-creation_date')
        questions_number = questions.count()
    else:
        questions = Question.objects.all().annotate(answers_count=Count('answer')).order_by('-creation_date')
        questions_number = Question.objects.all().count()

    answers_number = 0

    tags = {}
    for q in questions:
        answers_number += q.answer_set.count()

    page = request.GET.get('page', 1)
    paginator = Paginator(questions, 10)
    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)

    i = 1
    for q in questions:
        tags[i] = Tag.objects.filter(question=q).all()
        i = i + 1

    context = {
        'top_questions': top_questions,
        'latest_answers': latest_answers,
        'questions': questions,
        'tags': tags,
        'questions_number': questions_number,
        'answers_number': answers_number,
        'top_author': top_author,
        'text': text,
        'categories': categories,
        'all_tags': all_tags,
    }

    return render(request, 'qa/listing.html', context)


def like(request, selected_answer):
    if request.user.is_authenticated:
        method = request.GET.get('method', None)
        answer = get_object_or_404(Answer, id=selected_answer)

        if method == 'like':
            answer.like()
            answer.user.points += 2
            answer.user.save()
        elif method == 'dislike':
            answer.dislike()
            answer.user.points -= 2
            answer.user.save()

        Notification.objects.create(
            user=answer.user,
            object='react_a',
            id_object=answer.id
        )

        data = {
            'number': str(answer.likes),
            'id': '#numberLike' + str(answer.id),
            'div': '#divLike' + str(answer.id)
        }
        return JsonResponse(data)


@require_POST
def add_answer(request, qst_id):
    if request.user.is_authenticated:
        user = request.user
        question = get_object_or_404(Question, id=qst_id)

        if request.method == "POST":
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
                form = AnswerForm(request.POST)
                if form.is_valid():
                    cd = form.cleaned_data
                    content = cd['content']

                    answer = Answer.objects.create(question=question, content=content, user=user.profil)
                    user.profil.points += 5
                    user.profil.save()
                    message_success = 'Votre réponse a été ajouter'

                    Notification.objects.create(
                        object='answer',
                        id_object=answer.id,
                        user=question.user
                    )

                else:
                    message_success = 'Veuillez insérer un contenu valide'
            else:
                message_success = 'Le reCaptcha est invalide. Merci de réessayer.'

        request.session['message_answer'] = message_success
        return redirect('qa:question', qst_id)


def add_question(request):
    if request.user.is_authenticated:

        user = request.user.profil
        form = AddQuestionForm()
        status = 'get'
        message = 'None'
        qst = None

        if request.method == "POST":
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
                form = AddQuestionForm(request.POST)
                if form.is_valid():
                    cd = form.cleaned_data
                    title = cd['title']
                    content = cd['content']
                    category_q = request.POST.get('category')
                    category_q = get_object_or_404(Category, id=category_q)

                    qst = Question.objects.create(title=title, user=user, category=category_q, content=content)
                    qst.save()

                    tags = cd['tags']
                    tags = tags.split(',')
                    for tag in tags:
                        tag_add = Tag.objects.filter(title=tag)
                        if tag_add.count() > 0:
                            qst.tags.add(tag_add.first())
                        else:
                            qst.tags.add(Tag.objects.create(title=tag, create_by=user))

                    user.points += 10
                    user.save()

                    status = 'success'
                    message = 'Votre Question a été publier avec success'

                else:
                    status = 'form'
            else:
                status = 'recaptcha'
                message = 'Le reCaptcha est invalide. Merci de réessayer.'

        count_answer = Answer.objects.filter(user=user).count()
        top_questions = Question.objects.all().order_by("-views_number")[:3]

        context = {
            'categories': Category.objects.all().order_by('-title').exclude(title='Toutes les catégories'),
            'form': form,
            'user': user,
            'count_answer': count_answer,
            'top_questions': top_questions,
            'status': status,
            'message': message,
            'question': qst
        }
        return render(request, 'qa/post_question.html', context)
    else:
        return redirect('qa:home')


def delete_question(request, qst_id):
    if request.user.is_authenticated:
        qst = get_object_or_404(Question, id=qst_id)
        if request.user.profil == qst.user:
            qst.delete()
    return redirect('qa:all_questions')


def delete_answer(request, qst_id, answer_id):
    if request.user.is_authenticated:
        answer = get_object_or_404(Answer, id=answer_id)
        if request.user.profil == answer.user:
            answer.delete()
    return redirect('qa:question', qst_id=qst_id)


def profile(request, profile_id):
    user = get_object_or_404(Profil, id=profile_id)
    user.qa_view = user.qa_view + 1
    user.save()

    own_profile = False
    if request.user.is_authenticated:
        if request.user.profil == user:
            own_profile = True

    questions = Question.objects.filter(user=user)
    answers = Answer.objects.filter(user=user)
    articles = Article.objects.filter(author=user)

    activity = list(chain(questions, answers, articles))
    activity.sort(key=lambda x: x.creation_date, reverse=True)

    page = request.GET.get('page', 1)
    paginator = Paginator(activity, 10)
    try:
        activity = paginator.page(page)
    except PageNotAnInteger:
        activity = paginator.page(1)
    except EmptyPage:
        activity = paginator.page(paginator.num_pages)

    context = {
        'profile': user,
        'activities': activity,
        'own_profile': own_profile,
        'count_n': Notification.objects.filter(user=user, open=False).count()
    }

    return render(request, 'qa/profile.html', context)


def update_profile(request, profile_id):
    user = get_object_or_404(Profil, id=profile_id)

    if not request.user.is_authenticated:
        return redirect('qa:home')

    if request.user.profil != user:
        return redirect('qa:profile', profile_id=profile_id)

    form_profile = UpdatePImageForm()
    form_cover = UpdateCImageForm()
    form = UpdateProfileForm(initial={
        'first_name': user.user.first_name,
        'last_name': user.user.last_name,
        'job': user.fonction,
        'facebook': user.facebook,
        'twitter': user.twitter,
        'instagram': user.instagram,
        'youtube': user.youtube,
        'linkedIn': user.linkedin,
        'description': user.resume
    })

    if request.method == 'POST':

        method = request.POST.get('method', None)
        if method == 'profile':
            form_profile = UpdatePImageForm(request.POST, request.FILES)
            if form_profile.is_valid():
                image = Image.objects.create(
                    image=form_profile.cleaned_data['image_profile']
                )
                user.photo_profil = image
                user.save()

        elif method == 'cover':
            form_cover = UpdateCImageForm(request.POST, request.FILES)
            if form_cover.is_valid():
                image = Image.objects.create(
                    image=form_cover.cleaned_data['image_cover']
                )
                user.photo_couverture = image
                user.save()
        else:
            form = UpdateProfileForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                user.user.first_name = cd['first_name']
                user.user.last_name = cd['last_name']
                user.user.save()
                user.fonction = cd['job']
                user.facebook = cd['facebook']
                user.instagram = cd['instagram']
                user.twitter = cd['twitter']
                user.linkedin = cd['linkedIn']
                user.youtube = cd['youtube']
                user.resume = cd['description']
                user.save()
                return redirect('qa:profile', profile_id=profile_id)

    context = {
        'profile': user,
        'form': form,
        'form_profile': form_profile,
        'form_cover': form_cover,
    }

    return render(request, 'qa/update_profile.html', context)


def how_it_work(request):
    return render(request, 'qa/howItWork.html')


def contact(request):
    form = ContactForm()
    message = None

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
            form = ContactForm(request.POST)
            if form.is_valid():
                ContactMessage.objects.create(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    subject=form.cleaned_data['subject'],
                    message=form.cleaned_data['message']
                )
                message = 'success'
                form = ContactForm()
        else:
            message = 'recaptcha'

    context = {
        'form': form,
        'message': message
    }

    return render(request, 'qa/contact.html', context)


# BLOG VIEwS

def blog(request):

    articles = Article.objects.all().order_by('-creation_date')
    filter_field = request.GET.get('filter', 'date')
    if filter_field is not 'date':
        if filter_field == 'views':
            articles = Article.objects.all().order_by('-views', '-creation_date')
        elif filter_field == 'likes':
            articles = Article.objects.all().order_by('-likes', '-creation_date')
        elif filter_field == 'comment':
            articles = Article.objects.all().annotate(comment_count=Count('comment'))\
                .order_by('-comment_count', '-creation_date')

    page = request.GET.get('page', 1)
    paginator = Paginator(articles, 12)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    categories = Category.objects.all().annotate(article_count=Count('article')).order_by('-article_count')\
        .exclude(article_count=0)

    latest_articles = Article.objects.all().order_by('-creation_date')[:10]

    latest_images = Article.objects.all().order_by('-creation_date')[:12].values_list('image', flat=True)

    latest_comment = Comment.objects.all().order_by('-creation_date')[:5]

    top_tags = Tag.objects.all().annotate(article_count=Count('article')).order_by('-article_count')\
        .exclude(article_count=0)

    pro = False
    if request.user.is_authenticated:
        if request.user.profil.is_professional:
            pro = True

    context = {
        'articles': articles,
        'categories': categories,
        'latest_articles': latest_articles,
        'latest_images': latest_images,
        'latest_comment': latest_comment,
        'top_tags': top_tags,
        'filter': filter_field,
        'pro': pro
    }

    return render(request, 'qa/blog.html', context)


def blog_category(request, category_id):

    category_ = get_object_or_404(Category, id=category_id)

    articles = Article.objects.filter(category=category_)
    filter_field = request.GET.get('filter', 'date')
    if filter_field == 'views':
        articles = articles.order_by('-views', '-creation_date')
    elif filter_field == 'likes':
        articles = articles.order_by('-likes', '-creation_date')
    elif filter_field == 'comment':
        articles = articles.annotate(comment_count=Count('comment'))\
            .order_by('-comment_count', '-creation_date')
    else:
        articles = articles.order_by('-creation_date')

    page = request.GET.get('page', 1)
    paginator = Paginator(articles, 12)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    context = {
        'articles': articles,
        'filter': filter_field,
        'category': category_
    }

    return render(request, 'qa/blog_category.html', context)


def blog_tag(request, tag_id):

    tag_ = get_object_or_404(Tag, id=tag_id)
    Tracker.objects.create_from_request(request, tag_, tag_._meta.verbose_name)

    articles = Article.objects.filter(tags=tag_)
    filter_field = request.GET.get('filter', 'date')
    if filter_field == 'views':
        articles = articles.order_by('-views', '-creation_date')
    elif filter_field == 'likes':
        articles = articles.order_by('-likes', '-creation_date')
    elif filter_field == 'comment':
        articles = articles.annotate(comment_count=Count('comment'))\
            .order_by('-comment_count', '-creation_date')
    else:
        articles = articles.order_by('-creation_date')

    page = request.GET.get('page', 1)
    paginator = Paginator(articles, 12)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    context = {
        'articles': articles,
        'filter': filter_field,
        'tag': tag_
    }

    return render(request, 'qa/blog_tag.html', context)


def blog_post(request, article_id):

    article = get_object_or_404(Article, id=article_id)
    Tracker.objects.create_from_request(request, article, article._meta.verbose_name)
    article.add_view()

    categories = Category.objects.all().annotate(article_count=Count('article')).order_by('-article_count') \
        .exclude(article_count=0)

    latest_articles = Article.objects.all().order_by('-creation_date')[:10]

    latest_images = Image.objects.all().order_by('-add_date')[:12]

    latest_comment = Comment.objects.all().order_by('-creation_date')[:5]

    top_tags = Tag.objects.all().annotate(article_count=Count('article')).order_by('-article_count') \
        .exclude(article_count=0)

    message = 'get'

    if request.method == "POST":
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

            content = request.POST.get('content', '')
            if content != '':

                if request.user.is_authenticated:
                    comment = Comment.objects.create(user=request.user.profil, content=content, article=article)
                    Notification.objects.create(
                        object='comment',
                        id_object=comment.id,
                        user=article.author
                    )

                else:
                    full_name = request.POST.get('full_name', '')
                    email = request.POST.get('email', '')

                    if full_name != '':
                        if email != '':
                            comment = Comment.objects.create(full_name=full_name, email=email, content=content, article=article)
                            Notification.objects.create(
                                object='comment_x',
                                id_object=comment.id,
                                user=article.author
                            )
                        else:
                            message = 'Veuillez entrer un <strong>Email</strong> valide'
                    else:
                        message = 'Veuillez entrer un <strong>Nom</strong> valide'
            else:
                message = 'Veuillez entrer un <strong>Contenu</strong> valide'
        else:
            message = 'Recaptcha <strong>invalide</strong>, veuillez réssayer'

        if message == 'get':
            message = 'Votre <strong>commentaire</strong> a été publier avec succés'

    comments = article.comment_set.all().order_by('-creation_date')

    user_a_id = None
    pro = False
    if request.user.is_authenticated:
        user_a_id = request.user.profil.id
        if request.user.profil.is_professional:
            pro = True

    context = {
        'article': article,
        'categories': categories,
        'latest_articles': latest_articles,
        'latest_images': latest_images,
        'latest_comment': latest_comment,
        'top_tags': top_tags,
        'comments': comments,
        'message': message,
        'user_a_id': user_a_id,
        'pro': pro
    }

    return render(request, 'qa/blog_detail.html', context)


def like_post(request, post_id):

        method = request.GET.get('method', None)
        post = get_object_or_404(Article, id=post_id)

        if method == 'like':
            post.like()
        elif method == 'dislike':
            post.dislike()

        Notification.objects.create(
            user=post.author,
            object='post',
            id_object=post.id
        )

        data = {
            'number': str(post.likes) + ' J\'aime',
            'id': '#post_likes',
            'div': '#post_likes_form'
        }
        return JsonResponse(data)


def like_comment(request, comment_id):
    method = request.GET.get('method', None)
    comment = get_object_or_404(Comment, id=comment_id)

    if method == 'like':
        comment.like()
    elif method == 'dislike':
        comment.dislike()

    Notification.objects.create(
        user=comment.user,
        object='react_c',
        id_object=comment.id
    )

    data = {
        'number': str(comment.likes) + ' J\'aime',
        'id': '#likes' + str(comment.id),
        'div': '#comment_form_likes' + str(comment.id)
    }
    return JsonResponse(data)


def delete_comment(request, article_id, comment_id):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user.profil == comment.user:
            comment.delete()
    return redirect('qa:blog_post', article_id=article_id)


def delete_post(request, article_id):
    if request.user.is_authenticated:
        article = get_object_or_404(Article, id=article_id)
        if request.user.profil == article.author:
            article.delete()
    return redirect('qa:profile', profile_id=article.author.id)


def add_post(request):
    if request.user.is_authenticated:
        author = request.user.profil
        if request.user.profil.is_professional:
            form = AddPostForm()
            status = 'get'

            if request.method == "POST":

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

                    form = AddPostForm(request.POST, request.FILES)
                    if form.is_valid():
                        category_q = request.POST.get('category')
                        category_q = get_object_or_404(Category, id=category_q)

                        cd = form.cleaned_data
                        article = Article.objects.create(
                            title=cd['title'],
                            image=cd['image'],
                            content=cd['content'],
                            category=category_q,
                            author=author
                        )
                        author.points += 100

                        tags = cd['tags']
                        tags = tags.split(',')
                        for tag in tags:
                            tag_add = Tag.objects.filter(title=tag)
                            if tag_add.count() > 0:
                                article.tags.add(tag_add.first())
                            else:
                                article.tags.add(Tag.objects.create(title=tag, create_by=author))

                        return redirect('qa:blog_post', article_id=article.id)

                else:
                    status = 'recaptcha'

            latest_articles = Article.objects.all().order_by('-creation_date')[:5]

            context = {
                'form': form,
                'user': author,
                'status': status,
                'categories': Category.objects.all().order_by('-title').exclude(title='Toutes les catégories'),
                'latest_articles': latest_articles
            }

            return render(request, 'qa/post_blog.html', context)
    return redirect('qa:blog')


def update_post(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    if request.user.is_authenticated:
        author = request.user.profil
        if request.user.profil.is_professional:
            form = AddPostForm()
            status = 'get'

            if request.method == "POST":

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

                    form = AddPostForm(request.POST, request.FILES)
                    if form.is_valid():
                        category_q = request.POST.get('category')
                        category_q = get_object_or_404(Category, id=category_q)

                        cd = form.cleaned_data

                        article.title = cd['title']
                        article.image = cd['image']
                        article.content = cd['content']
                        article.category = category_q
                        article.author = author
                        article.creation_date = datetime.now()
                        article.save()

                        tags = cd['tags']
                        tags = tags.split(',')
                        for tag in tags:
                            tag_add = Tag.objects.filter(title=tag)
                            if tag_add.count() > 0:
                                article.tags.add(tag_add.first())
                            else:
                                article.tags.add(Tag.objects.create(title=tag, create_by=author))

                        return redirect('qa:blog_post', article_id=article.id)

                else:
                    status = 'recaptcha'

            latest_articles = Article.objects.all().order_by('-creation_date')[:5]

            tags_value = ''
            for t in article.tags.all():
                tags_value += t.title + ','
            form = AddPostForm(initial={
                'title': article.title,
                'content': article.content,
                'image': article.image,
                'tags': tags_value
            })

            context = {
                'form': form,
                'user': author,
                'status': status,
                'categories': Category.objects.all().order_by('-title').exclude(title='Toutes les catégories'),
                'latest_articles': latest_articles,
                'article': article,
                'article_count': Article.objects.filter(author=request.user.profil).count()
            }

            return render(request, 'qa/update_blog.html', context)
    return redirect('qa:blog')


def notification(request, profile_id):
    get_object_or_404(Profil, id=profile_id)
    if not request.user.is_authenticated:
        return redirect('qa:home')

    user = request.user.profil
    if user != Profil.objects.get(id=profile_id):
        return redirect('qa:profile', profile_id=profile_id)

    notifications = Notification.objects.filter(user=user).filter(open=False).order_by('-creation_date')

    list_n = []
    for n in notifications:
        n_ = NotificationH()
        n_.id = n.id
        if n.object == 'react_a':
            n_.icon = 'fa-thumbs-o-up'
            answer = Answer.objects.get(id=n.id_object)
            n_.content = '<a href=\"javascript:void(0);\">Une personne</a>'\
                   '<span> a réagit a votre réponse sur la question </span>' \
                   '<a href=\"/qa/question/' + str(answer.question.id) + '\">' + \
                   answer.question.title + '</a>' \
                   '<span>le ' + n.creation_date.strftime("%d-%m-%Y %H:%M:%S") + '</span>'
            list_n.append(n_)
        elif n.object == 'react_c':
            n_.icon = 'fa-thumbs-o-up'
            comment = Comment.objects.get(id=n.id_object)
            n_.content = '<a href=\"javascript:void(0);\">Une personne</a>'\
                   '<span> a réagit a votre commentaire sur l\'article </span>' \
                   '<a href=\"/qa/blog/article/' + str(comment.article.id) + '\">' + \
                   comment.article.title + '</a>' \
                   '<span>le ' + n.creation_date.strftime("%d-%m-%Y %H:%M:%S") + '</span>'
            list_n.append(n_)
        elif n.object == 'answer':
            n_.icon = 'fa-commenting'
            answer = Answer.objects.get(id=n.id_object)
            n_.content = '<a href=\"qa/profil/ ' + str(answer.user.id) + '\">' + answer.user.user.first_name.capitalize() + \
                   ' ' + answer.user.user.last_name.upper() + '</a>'\
                   '<span> a ajouté une réponse sur votre question </span>' \
                   '<a href=\"/qa/question/' + str(answer.question.id) + '\">' + \
                   answer.question.title + '</a>' \
                   '<span>le ' + n.creation_date.strftime("%d-%m-%Y %H:%M:%S") + '</span>'
            list_n.append(n_)
        elif n.object == 'comment':
            n_.icon = 'fa-comment'
            comment = Comment.objects.get(id=n.id_object)
            n_.content = '<a href=\"qa/profil/ ' + str(comment.user.id) + '\">' + comment.user.user.first_name.capitalize() + \
                   ' ' + comment.user.user.last_name.upper() + '</a>'\
                   '<span> a ajouté un commentaire sur votre article </span>' \
                   '<a href=\"/qa/blog/article/' + str(comment.article.id) + '\">' + \
                   comment.article.title + '</a>' \
                   '<span>le ' + n.creation_date.strftime("%d-%m-%Y %H:%M:%S") + '</span>'
            list_n.append(n_)
        elif n.object == 'comment_x':
            n_.icon = 'fa-comment'
            comment = Comment.objects.get(id=n.id_object)
            n_.content = '<a href=\"javascript:void(0);\">' + comment.full_name + '</a>' \
                    '<span> a ajouté un commentaire sur votre article </span>' \
                    '<a href=\"/qa/blog/article/' + str(comment.article.id) + '\">' + \
                   comment.article.title + '</a>' \
                    '<span>le ' + n.creation_date.strftime("%d-%m-%Y %H:%M:%S") + '</span>'
            list_n.append(n_)
        elif n.object == 'post':
            n_.icon = 'fa-smile-o'
            article = Article.objects.get(id=n.id_object)
            n_.content = '<a href=\"javascript:void(0);\">Une personne</a>'\
                   '<span> a réagit a votre article </span>' \
                   '<a href=\"/qa/blog/article/' + str(article.id) + '\">' + \
                   article.title + '</a><span>le ' + n.creation_date.strftime("%d-%m-%Y %H:%M:%S") + '</span>'
            list_n.append(n_)

    page = request.GET.get('page', 1)
    paginator = Paginator(list_n, 25)
    try:
        list_n = paginator.page(page)
    except PageNotAnInteger:
        list_n = paginator.page(1)
    except EmptyPage:
        list_n = paginator.page(paginator.num_pages)

    context = {
        'profile': user,
        'notifications': list_n,
        'count': Notification.objects.filter(user=user, open=False).count()
    }

    return render(request, 'qa/notification.html', context)


def notification_open(request, profile_id, n_id):
    n = get_object_or_404(Notification, id=n_id)
    p = get_object_or_404(Profil, id=profile_id)

    count = Notification.objects.filter(user=p, open=False).count()

    if request.user.is_authenticated:
        if request.user.profil == p:
            n.open = True
            n.save()
            data = {
                "id": '#countNotification',
                "number": count - 1,
                'div': '#no'+str(n_id)
            }
            return JsonResponse(data)


def all_notification_open(request, profile_id):
    p = get_object_or_404(Profil, id=profile_id)

    if request.user.is_authenticated:
        if request.user.profil == p:
            for n in Notification.objects.filter(user=p, open=False):
                n.open = True
                n.save()

    return redirect('qa:profile', profile_id=profile_id)


class NotificationH(object):
    id = 0
    content = ''
    icon = ''

    def __str__(self):
        return self.id


# Signal Views
def signal_question(request, qst_id):
    question = get_object_or_404(Question, id=qst_id)

    profile_ = None
    if request.user.is_authenticated:
        profile_ = request.user.profil

    SignalQuestion.objects.create(
        profile=profile_,
        question=question
    )

    return redirect('qa:question', qst_id)


def signal_answer(request, qst_id, answer_id):
    question = get_object_or_404(Question, id=qst_id)
    answer = get_object_or_404(Answer, id=answer_id)

    profile_ = None
    if request.user.is_authenticated:
        profile_ = request.user.profil

    SignalAnswer.objects.create(
        profile=profile_,
        answer=answer
    )

    return redirect('qa:question', question.id)


def signal_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)

    profile_ = None
    if request.user.is_authenticated:
        profile_ = request.user.profil

    SignalArticle.objects.create(
        profile=profile_,
        article=article
    )

    return redirect('qa:blog_post', article_id)


def signal_comment(request, article_id, comment_id):
    article = get_object_or_404(Article, id=article_id)
    comment = get_object_or_404(Comment, id=comment_id)

    profile_ = None
    if request.user.is_authenticated:
        profile_ = request.user.profil

    SignalComment.objects.create(
        profile=profile_,
        comment=comment
    )

    return redirect('qa:blog_post', article.id)


def share_question(request, id):
    question = get_object_or_404(Question, id=id)
    question.add_share()
    return HttpResponse('')

def share_article(request, id):
    article = get_object_or_404(Article, id=id)
    article.add_share()
    return HttpResponse('')
