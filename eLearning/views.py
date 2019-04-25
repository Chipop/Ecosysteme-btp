from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm

from .models import *
from .forms import *
from django.core.mail import send_mail
from main_app.models import Profil, Image
from django.db.models import Avg, F, Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index(request):
    # all_courses = Course.objects.filter(approved=True, active=True)[:10]
    all_courses = Formation.objects.filter(course__active=True, course__approved=True).values('course__id') \
        .annotate(number=Count('id')).order_by('-number')
    courses = []
    for c in all_courses:
        c = Course.objects.get(id=c['course__id'])
        el = {'c': c}
        ratting = Ratting.objects.filter(course=c).values('course_id').annotate(ratting=Avg('value'),
                                                                                number=Count('id'))
        if ratting:
            el['ratting'] = ratting[0]['ratting']
            el['rattingInt'] = int(el['ratting'])
            el['number'] = ratting[0]['number']
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0
            el['number'] = 0
        sale = c.elearning_sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
        if sale.exists():
            el['sale'] = sale[0]
        else:
            el['sale'] = None
        courses.append(el)
    categories = Course.objects.filter(active=True, approved=True).values('category__category').annotate(
        number=Count('id'), c=F('category__category')).order_by('number').reverse()
    for cat in categories:
        cat['c'] = Category.objects.get(pk=cat['c'])
    context = {
        'courses': courses,
        'categories': categories
    }
    return render(request, 'eLearning/index.html', context)


def search(request):
    if request.method != "GET":
        return HttpResponseRedirect(reverse('eLearning:index'))
    else:
        categories = Category.objects.all()
        key_word = request.GET.get('q', '')
        selected_category = request.GET.get('filter_category', '0')
        selected_level = request.GET.get('filter_level', '0')
        selected_paying = request.GET.get('filter_paying', '0')
        sort = request.GET.get('sort', 'all')
        type_list = request.GET.get('type_list', '')
        is_filtering = False
        if selected_category != '0' or selected_level != '0' or selected_paying != '0' or sort != 'all' or type_list != '':
            is_filtering = True
        if sort == 'popular':
            courses_result = Formation.objects.filter(Q(course__name__icontains=key_word)
                                                      | Q(course__description__icontains=key_word)
                                                      | Q(course__teacher__user__first_name__icontains=key_word)
                                                      | Q(course__teacher__user__last_name__icontains=key_word)
                                                      | Q(course__teacher__teacher_title__icontains=key_word)
                                                      | Q(course__category__name__icontains=key_word)
                                                      | Q(course__category__category__name__icontains=key_word),
                                                      course__active=True, course__approved=True).\
                values('course__id', 'course__is_free', 'course__level', 'course__category__category_id') \
                .annotate(number=Count('id')).order_by('-number')
            if selected_category != '0':
                courses_result = courses_result.filter(course__category__category__id=selected_category)
            if selected_level != '0':
                courses_result = courses_result.filter(course__level__iexact=selected_level)
            if selected_paying == '1':
                courses_result = courses_result.filter(course__is_free=True)
            if selected_paying == '2':
                courses_result = courses_result.filter(course__is_free=False)
        elif sort == 'review':
            courses_result = Ratting.objects.filter(Q(course__name__icontains=key_word)
                                                    | Q(course__description__icontains=key_word)
                                                    | Q(course__teacher__user__first_name__icontains=key_word)
                                                    | Q(course__teacher__user__last_name__icontains=key_word)
                                                    | Q(course__teacher__teacher_title__icontains=key_word)
                                                    | Q(course__category__name__icontains=key_word)
                                                    | Q(course__category__category__name__icontains=key_word),
                                                    course__active=True, course__approved=True). \
                values('course__id', 'course__is_free', 'course__level', 'course__category__category_id') \
                .annotate(avg=Avg('value')).order_by('-avg')
            if selected_category != '0':
                courses_result = courses_result.filter(course__category__category__id=selected_category)
            if selected_level != '0':
                courses_result = courses_result.filter(course__level__iexact=selected_level)
            if selected_paying == '1':
                courses_result = courses_result.filter(course__is_free=True)
            if selected_paying == '2':
                courses_result = courses_result.filter(course__is_free=False)
        else:
            courses_result = Course.objects.filter(Q(name__icontains=key_word) | Q(description__icontains=key_word)
                                                   | Q(teacher__user__first_name__icontains=key_word)
                                                   | Q(teacher__user__last_name__icontains=key_word)
                                                   | Q(teacher__teacher_title__icontains=key_word)
                                                   | Q(category__name__icontains=key_word)
                                                   | Q(category__category__name__icontains=key_word), active=True,
                                                   approved=True)
            if selected_category != '0':
                courses_result = courses_result.filter(category__category__id=selected_category)
            if selected_level != '0':
                courses_result = courses_result.filter(level__iexact=selected_level)
            if selected_paying == '1':
                courses_result = courses_result.filter(is_free=True)
            if selected_paying == '2':
                courses_result = courses_result.filter(is_free=False)
            if sort == 'latest':
                courses_result = courses_result.order_by('-date_add')
        courses = []
        for c in courses_result:
            if sort == 'popular' or sort == 'review':
                c = Course.objects.get(id=c['course__id'])
            el = {'c': c}
            ratting = Ratting.objects.filter(course=c).values('course_id').annotate(ratting=Avg('value'),
                                                                                    number=Count('id'))
            if ratting:
                el['ratting'] = ratting[0]['ratting']
                el['rattingInt'] = int(el['ratting'])
                el['number'] = ratting[0]['number']
            else:
                el['rattingInt'] = 0
                el['ratting'] = 0
                el['number'] = 0
            sale = c.elearning_sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
            if sale.exists():
                el['sale'] = sale[0]
            else:
                el['sale'] = None
            el['number_chapters'] = Chapter.objects.filter(part__course=c).count()
            courses.append(el)
            # if sort == 'all' and type_list == 'grid':
            #       ResultSearch.objects.create(key_word=key_word, course=c)
        page = request.GET.get('page', 1)
        paginator = Paginator(courses, 9)
        try:
            courses_page = paginator.page(page)
        except PageNotAnInteger:
            courses_page = paginator.page(1)
        except EmptyPage:
            courses_page = paginator.page(paginator.num_pages)
        context = {
            'sort': sort,
            'selected_category': int(selected_category),
            'selected_level': selected_level,
            'selected_paying': int(selected_paying),
            'type': type_list,
            'key_word': key_word,
            'is_filtering': is_filtering,

            'categories': categories,
            'courses': courses_page
        }
        if type_list in ('list', ''):
            return render(request, 'eLearning/search-list.html', context)
        elif type_list == 'grid':
            return render(request, 'eLearning/search-grid.html', context)
        else:
            return get_object_or_404(Course, pk=-1)


def courses_list(request):
    sort = request.GET.get('sort', 'all')
    selected_categories = list(map(int, request.GET.getlist('selected_categories', [])))
    selected_revues = list(map(int, request.GET.getlist('selected_revues', [])))
    selected_level = request.GET.get('filter_level', '0')
    selected_paying = request.GET.get('filter_paying', '0')
    selected_category = request.GET.get('filter_category', '0')
    type_list = request.GET.get('type_list', '')
    is_filtering = False
    if selected_category != '0' or selected_level != '0' or selected_paying != '0' or sort != 'all' or type_list != '' or len(
            selected_categories) > 0 or len(selected_revues) > 0:
        is_filtering = True
    if sort == 'popular':
        courses_result = Formation.objects.filter(course__active=True, course__approved=True).values('course__id',
        'course__is_free', 'course__level', 'course__category__category_id', 'course__category_id')\
            .annotate(number=Count('id')).order_by('-number')
        if selected_category != '0':
            courses_result = courses_result.filter(course__category__category_id=selected_category)

        if selected_level != '0':
            courses_result = courses_result.filter(course__level__iexact=selected_level)

        if selected_paying == '1':
            courses_result = courses_result.filter(course__is_free=True)

        if selected_paying == '2':
            courses_result = courses_result.filter(course__is_free=False)

        if selected_categories:
            courses_result = courses_result.filter(course__category_id__in=selected_categories)
    elif sort == 'review':
        courses_result = Ratting.objects.filter(course__active=True, course__approved=True, ).values('course__id',
        'course__is_free', 'course__level', 'course__category_id', 'course__category__category_id')\
            .annotate(avg=Avg('value')).order_by('-avg')
        if selected_category != '0':
            courses_result = courses_result.filter(course__category__category_id=selected_category)

        if selected_level != '0':
            courses_result = courses_result.filter(course__level__iexact=selected_level)

        if selected_paying == '1':
            courses_result = courses_result.filter(course__is_free=True)

        if selected_paying == '2':
            courses_result = courses_result.filter(course__is_free=False)

        if selected_categories:
            courses_result = courses_result.filter(course__category_id__in=selected_categories)
    else:
        courses_result = Course.objects.filter(active=True, approved=True)
        # Filter
        if selected_category != '0':
            courses_result = courses_result.filter(category__category__id=selected_category)

        if sort == 'latest':
            courses_result = courses_result.order_by('-date_add')

        if selected_categories:
            courses_result = courses_result.filter(category__category__id__in=selected_categories)

        if selected_level != '0':
            courses_result = courses_result.filter(level__iexact=selected_level)

        if selected_paying == '1':
            courses_result = courses_result.filter(is_free=True)

        if selected_paying == '2':
            courses_result = courses_result.filter(is_free=False)

    courses = []
    for c in courses_result:
        if sort in ['popular', 'review']:
            c = Course.objects.get(id=c['course__id'])
        el = {'c': c}
        ratting = Ratting.objects.filter(course=c).values('course_id').annotate(ratting=Avg('value'),
                                                                                number=Count('id'))
        if ratting:
            el['ratting'] = ratting[0]['ratting']
            el['rattingInt'] = int(el['ratting'])
            el['number'] = ratting[0]['number']
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0
            el['number'] = 0
        if selected_revues and el['rattingInt'] not in selected_revues and el['rattingInt'] + 1 not in selected_revues:
            continue
        sale = c.elearning_sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
        if sale.exists():
            el['sale'] = sale[0]
        else:
            el['sale'] = None
        courses.append(el)
    categories = Course.objects.filter(active=True, approved=True).values('category__category').annotate(
        number=Count('id'), pk=F('category__category'), name=F('category__category__name'))
    revues = Ratting.objects.filter(course__approved=True, course__active=True).values('value') \
        .annotate(number=Count('course__pk')).order_by('value').reverse()
    page = request.GET.get('page', 1)
    paginator = Paginator(courses, 10)
    try:
        courses_page = paginator.page(page)
    except PageNotAnInteger:
        courses_page = paginator.page(1)
    except EmptyPage:
        courses_page = paginator.page(paginator.num_pages)
    context = {
        'sort': sort,
        'selected_category': int(selected_category),
        'selected_level': selected_level,
        'selected_paying': int(selected_paying),
        'type': type_list,
        'selected_categories': selected_categories,
        'selected_revues': selected_revues,
        'is_filtering': is_filtering,

        'categories': categories,
        'revues': revues,
        'courses': courses_page
    }
    if type_list in ('list', ''):
        return render(request, 'eLearning/courses-list-sidebar.html', context)
    elif type_list == 'grid':
        return render(request, 'eLearning/courses-grid-sidebar.html', context)
    else:
        return get_object_or_404(Course, pk=-1)


def course(request, id_course=0):
    displayed_course = get_object_or_404(Course, pk=id_course)
    if not displayed_course.approved or not displayed_course.active:
        return HttpResponseRedirect(reverse('eLearning:index'))
    displayed_course.add_view()
    sale = displayed_course.elearning_sale_set.filter(date_end__gte=timezone.now()).order_by('date_end').first()
    ratting = Course.objects.filter(pk=id_course).aggregate(ratting=Avg('elearning_ratting_set__value'))['ratting']
    teacher_ratting = Course.objects.filter(teacher=displayed_course.teacher) \
        .aggregate(ratting=Avg('elearning_ratting_set__value'))['ratting']
    teacher_ratting_count = Ratting.objects.filter(course__teacher=displayed_course.teacher).count()
    if teacher_ratting:
        teacher_ratting_int = int(teacher_ratting)
    else:
        teacher_ratting = 0
        teacher_ratting_int = 0
    number_reviews = Ratting.objects.filter(course__id=id_course).count()
    if ratting:
        ratting_int = int(ratting)
        five = (Ratting.objects.filter(course__id=id_course, value=5).count() * 100) / number_reviews
        four = (Ratting.objects.filter(course__id=id_course, value=4).count() * 100) / number_reviews
        three = (Ratting.objects.filter(course__id=id_course, value=3).count() * 100) / number_reviews
        two = (Ratting.objects.filter(course__id=id_course, value=2).count() * 100) / number_reviews
        one = (Ratting.objects.filter(course__id=id_course, value=1).count() * 100) / number_reviews
    else:
        ratting = ratting_int = five = four = three = two = one = 0
    number_chapters = Chapter.objects.filter(part__course=displayed_course).count()
    allow = False

    progress = last_chapter_id = 0
    list_seen = list_quiz = []
    if request.user.is_authenticated:
        profil = request.user.profil
        if Formation.objects.filter(student=profil, course=displayed_course).exists():
            allow = True
            number_chapters_seen = Progress.objects.filter(chapter__part__course=displayed_course,
                                                           student=profil).count()
            if number_chapters > 0:
                progress = (number_chapters_seen * 100) / number_chapters
            if number_chapters_seen > 0:
                last_chapter_id = Progress.objects.filter(chapter__part__course=displayed_course,
                                                          student=profil).order_by('date_add').last().chapter.pk
                seen_ids = Progress.objects.filter(chapter__part__course=displayed_course,
                                                   student=profil).values('chapter_id')
                list_seen = [entry['chapter_id'] for entry in seen_ids]
                list_quiz = list(map(int, Answer.objects.filter(student=profil, exam__part__course=displayed_course).values_list('exam_id', flat=True)))

    associated_courses = displayed_course.teacher.elearning_course_set.exclude(pk=displayed_course.pk).order_by("date_add")[:3]
    courses = []
    for c in associated_courses:
        el = {'c': c}
        rating = Ratting.objects.filter(course=c).values('course_id').annotate(ratting=Avg('value'), number=Count('id'))
        if rating:
            el['ratting'] = rating[0]['ratting']
            el['rattingInt'] = int(el['ratting'])
            el['number'] = rating[0]['number']
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0
            el['number'] = 0

        sale = c.elearning_sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
        if sale.exists():
            el['sale'] = sale[0]
        else:
            el['sale'] = None
        courses.append(el)

    context = {
        'course': displayed_course,
        'sale': sale,
        'ratting': ratting,
        'rattingInt': ratting_int,
        'teacher_ratting': teacher_ratting,
        'teacher_rattingInt': teacher_ratting_int,
        'teacher_ratting_count': teacher_ratting_count,
        'number_chapters': number_chapters,
        'number_reviews': number_reviews,
        'five': str(five).replace(',', '.'),
        'four': str(four).replace(',', '.'),
        'three': str(three).replace(',', '.'),
        'two': str(two).replace(',', '.'),
        'one': str(one).replace(',', '.'),
        'progress': str(progress).replace(',', '.'),
        'allow': allow,
        'last_chapter_id': last_chapter_id,
        'list_seen': list_seen,
        'list_quiz': list_quiz,
        'associated_courses': courses,
        'counter': Counter()
    }
    return render(request, 'eLearning/course-detail.html', context)


def quiz(request, id_quiz=0):
    displayed_quiz = get_object_or_404(Exam, pk=id_quiz)
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    questions = []
    result = None
    if request.method == "POST":
        correct_answers_number = 0
        for question in displayed_quiz.elearning_question_set.all():
            el = {'el': question}
            my_answers = list(map(int, request.POST.getlist("question"+str(question.pk), [])))
            correct_answers = list(question.elearning_choice_set.filter(is_correct=True).values_list('pk', flat=True))
            el['my_answers'] = my_answers
            if my_answers == correct_answers:
                correct_answers_number += 1
                el['right_answer'] = True
            else:
                el['right_answer'] = False
            questions.append(el)
        result = correct_answers_number * 100 / len(questions)
        answer = Answer.objects.get_or_create(student=request.user.profil, exam=displayed_quiz)
        answer[0].score = int(result)
        answer[0].save()
    else:
        for question in displayed_quiz.elearning_question_set.all():
            questions.append({'el': question})
    last_result = None
    last_answer = Answer.objects.filter(student=request.user.profil, exam=displayed_quiz)
    if last_answer.exists():
        last_result = last_answer.first().score
    context = {
        'quiz': displayed_quiz,
        'questions': questions,
        'method': request.method,
        'result': result,
        'last_result': last_result
    }
    return render(request, 'eLearning/quiz.html', context)


def teacher(request, id_teacher=0):
    displayed_teacher = get_object_or_404(Profil, pk=id_teacher)
    if not displayed_teacher.is_teacher:
        return HttpResponseRedirect(reverse('eLearning:index'))
    displayed_teacher.view_teacher += 1
    displayed_teacher.save()
    ratting = Course.objects.filter(teacher_id=id_teacher).aggregate(ratting=Avg('elearning_ratting_set__value'))['ratting']
    number_reviews = Ratting.objects.filter(course__teacher_id=id_teacher).count()
    if ratting:
        ratting_int = int(ratting)
    else:
        ratting = ratting_int = 0

    courses_result = Course.objects.filter(approved=True, active=True, teacher_id=id_teacher)
    courses = []
    for c in courses_result:
        el = {'c': c}
        ratting_course = Ratting.objects.filter(course=c).values('course_id').annotate(ratting=Avg('value'))
        if ratting_course:
            el['ratting'] = ratting_course[0]['ratting']
            el['rattingInt'] = int(el['ratting'])
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0
        courses.append(el)
    page = request.GET.get('page', 1)
    paginator = Paginator(courses, 10)
    try:
        courses_page = paginator.page(page)
    except PageNotAnInteger:
        courses_page = paginator.page(1)
    except EmptyPage:
        courses_page = paginator.page(paginator.num_pages)
    context = {
        'teacher': displayed_teacher,
        'ratting': ratting,
        'rattingInt': ratting_int,
        'number_reviews': number_reviews,
        'courses': courses_page,
        'form': SendMessageForm()
    }
    return render(request, 'eLearning/teacher-detail.html', context)


def category(request, id_category=0):
    sort = request.GET.get('sort', 'all')
    selected_level = request.GET.get('filter_level', '0')
    selected_paying = request.GET.get('filter_paying', '0')
    selected_category = get_object_or_404(Category, pk=id_category)
    selected_categories = list(map(int, request.GET.getlist('selected_categories', [])))
    selected_revues = list(map(int, request.GET.getlist('selected_revues', [])))
    type_list = request.GET.get('type_list', '')
    is_filtering = False
    if selected_level != '0' or selected_paying != '0' or sort != 'all' or type_list != '' or len(
            selected_categories) > 0 or len(selected_revues) > 0:
        is_filtering = True
    if sort == 'popular':
        courses_result = Formation.objects.filter(course__active=True, course__approved=True,
            course__category__category=selected_category).values('course__id', 'course__is_free', 'course__level',
            'course__category_id').annotate(number=Count('id')).order_by('-number')
        if selected_level != '0':
            courses_result = courses_result.filter(course__level__iexact=selected_level)

        if selected_paying == '1':
            courses_result = courses_result.filter(course__is_free=True)

        if selected_paying == '2':
            courses_result = courses_result.filter(course__is_free=False)

        if selected_categories:
            courses_result = courses_result.filter(course__category_id__in=selected_categories)
    elif sort == 'review':
        courses_result = Ratting.objects.filter(course__active=True, course__approved=True,
            course__category__category=selected_category).values('course__id', 'course__is_free', 'course__level',
             'course__category_id').annotate(avg=Avg('value')).order_by('-avg')
        if selected_level != '0':
            courses_result = courses_result.filter(course__level__iexact=selected_level)

        if selected_paying == '1':
            courses_result = courses_result.filter(course__is_free=True)

        if selected_paying == '2':
            courses_result = courses_result.filter(course__is_free=False)

        if selected_categories:
            courses_result = courses_result.filter(course__category_id__in=selected_categories)
    else:
        courses_result = Course.objects.filter(active=True, approved=True, category__category=selected_category)

        if selected_level != '0':
            courses_result = courses_result.filter(level__iexact=selected_level)

        if selected_paying == '1':
            courses_result = courses_result.filter(is_free=True)

        if selected_paying == '2':
            courses_result = courses_result.filter(is_free=False)

        if sort == 'latest':
            courses_result = courses_result.order_by('-date_add')
        if selected_categories:
            courses_result = courses_result.filter(category__id__in=selected_categories)

    courses = []
    for c in courses_result:
        if sort in ('popular', 'review'):
            c = Course.objects.get(id=c['course__id'])
        el = {'c': c}
        ratting = Ratting.objects.filter(course=c).values('course_id').annotate(ratting=Avg('value'),
                                                                                number=Count('id'))
        if ratting:
            el['ratting'] = ratting[0]['ratting']
            el['rattingInt'] = int(el['ratting'])
            el['number'] = ratting[0]['number']
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0
            el['number'] = 0
        if selected_revues and el['rattingInt'] not in selected_revues and el['rattingInt'] + 1 not in selected_revues:
            continue
        sale = c.elearning_sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
        if sale.exists():
            el['sale'] = sale[0]
        else:
            el['sale'] = None
        courses.append(el)
    categories = Course.objects.filter(active=True, approved=True, category__category_id=id_category). \
        values('category').annotate(number=Count('id'), pk=F('category'), name=F('category__name'))
    revues = Ratting.objects.filter(course__approved=True, course__active=True,
                                    course__category__category_id=id_category).values('value')\
        .annotate(number=Count('course__pk')).order_by('-value')

    category_ = Category.objects.get(id=id_category)

    page = request.GET.get('page', 1)
    paginator = Paginator(courses, 10)
    try:
        courses_page = paginator.page(page)
    except PageNotAnInteger:
        courses_page = paginator.page(1)
    except EmptyPage:
        courses_page = paginator.page(paginator.num_pages)
    context = {
        'sort': sort,
        'selected_category': id_category,
        'selected_level': selected_level,
        'selected_paying': int(selected_paying),
        'type': type_list,
        'selected_categories': selected_categories,
        'selected_revues': selected_revues,
        'is_filtering': is_filtering,

        'categories': categories,
        'revues': revues,
        'courses': courses_page,
        'category': category_
    }
    if type_list in ('list', ''):
        return render(request, 'eLearning/courses-category-list-sidebar.html', context)
    elif type_list == 'grid':
        return render(request, 'eLearning/courses-category-grid-sidebar.html', context)
    else:
        return get_object_or_404(Course, pk=-1)


def wish_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    courses_result = WishList.objects.filter(user=request.user.profil)

    courses = []
    for c in courses_result:
        c = c.course
        el = {'c': c}
        ratting = Ratting.objects.filter(course=c).values('course_id').annotate(ratting=Avg('value'),
                                                                                number=Count('id'))
        if ratting:
            el['ratting'] = ratting[0]['ratting']
            el['rattingInt'] = int(el['ratting'])
            el['number'] = ratting[0]['number']
        else:
            el['rattingInt'] = 0
            el['ratting'] = 0
            el['number'] = 0
        sale = c.elearning_sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
        if sale.exists():
            el['sale'] = sale[0]
        else:
            el['sale'] = None
        courses.append(el)
    context = {
        'courses': courses
    }
    return render(request, 'eLearning/wish-list.html', context)


def cart(request, message_error=""):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    total = 0
    user = request.user
    courses_result = Cart.objects.filter(user=user.profil)
    courses = []
    for c in courses_result:
        el = {'id': c.id}
        c = c.course
        el['c'] = c
        sale = c.elearning_sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
        if sale.exists():
            el['sale'] = sale[0]
            total += sale[0].new_price()
        else:
            el['sale'] = None
            total += c.price
        courses.append(el)
    context = {
        'courses': courses,
        'total': total,
        'message_error': message_error
    }
    return render(request, 'eLearning/cart-1.html', context)


def student_dashboard(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    profil = request.user.profil
    courses_result = Formation.objects.filter(student=profil)
    courses = []
    progress_total = 0
    progress_number = 0
    selected_category = request.GET.get('filterCategory', '0')
    selected_teacher = request.GET.get('filterTeacher', '0')
    selected_progress = request.GET.get('filterProgress', '0')
    if selected_category != '0':
        courses_result = courses_result.filter(course__category__category_id=selected_category)
    if selected_teacher != '0':
        courses_result = courses_result.filter(course__teacher_id=selected_teacher)
    for c in courses_result:
        el = {'id': c.id, 'date': c.date_start}
        c = c.course
        el['c'] = c
        progress = 0
        number_chapters = Chapter.objects.filter(part__course=c).count()
        number_chapters_seen = Progress.objects.filter(chapter__part__course=c,
                                                       student=profil).count()
        if number_chapters > 0:
            progress = (number_chapters_seen * 100) / number_chapters
        progress_number += 1
        progress_total += progress
        el['progress'] = str(progress).replace(',', '.')
        if selected_progress == '0':
            courses.append(el)
        elif selected_progress == '1' and progress == 0:
            courses.append(el)
        elif selected_progress == '2' and progress != 0:
            courses.append(el)
        elif selected_progress == '3' and progress == 100:
            courses.append(el)

    try:
        progress_avg = progress_total / progress_number
    except ZeroDivisionError:
        progress_avg = 0

    teachers = Formation.objects.filter(student=profil).values(teacher_id=F('course__teacher_id'),
                                                               teacher_last_name=F('course__teacher__user__last_name'),
                                                               teacher_first_name=F(
                                                                   'course__teacher__user__first_name')).distinct()
    categories = Formation.objects.filter(student=profil).values(category_id=F('course__category__category_id'),
                                                                 category_name=F(
                                                                     'course__category__category__name')).distinct()

    context = {
        'courses': courses,
        'progress_avg': str(progress_avg).replace(',', '.'),
        'teachers': teachers,
        'categories': categories,
        'selected_category': int(selected_category),
        'selected_teacher': int(selected_teacher),
        'selected_progress': int(selected_progress)
    }
    return render(request, 'eLearning/student-dashboard.html', context)


def student_messages(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))

    messages = MessageToStudent.objects.filter(parent_message__student=request.user.profil)
    page = request.GET.get('page', 1)
    filter_by = request.GET.get('filter_by', 1)
    order_by = request.GET.get('order_by', '1')

    if filter_by == '2':
        messages = messages.filter(is_read=False)
    if filter_by == '3':
        messages = messages.filter(is_read=True)

    if order_by == '1' or order_by == '2':
        messages = messages.order_by('-date_add')
    if order_by == '3':
        messages = messages.order_by('date_add')
    if order_by == '4':
        messages = messages.order_by('parent_message__teacher__user__last_name',
                                     'parent_message__teacher__user__first_name')
    if order_by == '5':
        messages = messages.order_by('-parent_message__teacher__user__last_name',
                                     '-parent_message__teacher__user__first_name')

    paginator = Paginator(messages, 10)  # to turn to 10
    try:
        messages_page = paginator.page(page)
    except PageNotAnInteger:
        messages_page = paginator.page(1)
    except EmptyPage:
        messages_page = paginator.page(paginator.num_pages)

    context = {
        'messages': messages_page,
        'order_by': order_by,
        'filter_by': filter_by,
    }
    return render(request, 'eLearning/student-messages.html', context)


def upgrade(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    if request.method == "POST":
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('telephone', '')
        facebook = request.POST.get('facebook', '')
        youtube = request.POST.get('youtube', '')
        instagram = request.POST.get('instagram', '')
        linkedin = request.POST.get('linkedin', '')
        twitter = request.POST.get('twitter', '')
        teacher_title = request.POST.get('teacher_title', '')
        biography = request.POST.get('biography', '')
        photo_profil = request.FILES.get('photo_profil', None)
        cv = request.FILES.get('cv', None)
        user = request.user
        if first_name != '':
            user.first_name = first_name
        if last_name != '':
            user.last_name = last_name
        if email != '':
            user.email = email
        user.save()
        profil = user.profil
        if phone != '':
            profil.tel = phone
        if facebook != '':
            profil.facebook = facebook
        if youtube != '':
            profil.youtube = youtube
        if instagram != '':
            profil.instagram = instagram
        if linkedin != '':
            profil.linkedin = linkedin
        if twitter != '':
            profil.twitter = twitter
        if teacher_title != '':
            profil.teacher_title = teacher_title
        if biography != '':
            profil.biography = biography
        if photo_profil is not None:
            img = Image.objects.create(image=photo_profil)
            profil.photo_profil = img
        if cv is not None:
            profil.cv = cv
        profil.request_teacher = True
        profil.save()
    return render(request, 'eLearning/upgrade.html')


def checkout(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    if request.method != "POST":
        return HttpResponseRedirect(reverse('eLearning:cart'))
    else:
        user = request.user.profil
        order = Order.objects.create(student=user)
        coupon_values = request.POST.getlist('coupon_values', [])
        courses = []
        total = 0
        courses_result = Cart.objects.filter(user=user)
        for c in courses_result:
            c = c.course
            coupons = Coupon.objects.filter(
                (Q(is_general=True) | (Q(is_general=False) & Q(course=c))) & Q(value__in=coupon_values) & Q(
                    used=False)).order_by("-percentage")
            if coupons.exists() and not c.is_free:
                el = {'id': c.id}
                coupon = coupons.first()
                percentage = coupon.percentage
                el['percentage'] = percentage
                el['price'] = c.price - (c.price * percentage / 100)
                total += el['price']
                courses.append(el)
                OrderLine.objects.create(course=c, order=order, amount=el['price'], coupon=coupon)
            else:
                sale = c.elearning_sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
                if sale.exists():
                    price = sale[0].new_price()
                else:
                    price = c.price
                total += price
                OrderLine.objects.create(course=c, order=order, amount=price)
        order.amount = total
        order.save()
        request.session['order_id'] = order.pk
        if order.amount == 0:
            return HttpResponseRedirect(reverse("eLearning:cart"))
        paypal_dict = {
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "amount": str(order.amount / 10),
            "item_name": "Commande #{}".format(order.id),
            "invoice": str(order.id),
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return": request.build_absolute_uri(reverse('eLearning:paypal_done')),
            "cancel_return": request.build_absolute_uri(reverse('eLearning:paypal_cancel')),
        }

        # Create the instance.
        form = PayPalPaymentsForm(initial=paypal_dict)
    context = {
        'order': order,
        'form': form
    }
    return render(request, 'eLearning/cart-2.html', context)


@csrf_exempt
def paypal_done(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    return render(request, 'eLearning/cart-3.html')


@csrf_exempt
def paypal_cancel(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('main_app:log_in'))
    if 'order_id' in request.session:
        order_id = request.session['order_id']
        order = Order.objects.filter(pk=order_id)
        if order.exists():
            order.first().delete()
            del request.session['order_id']
    message_error = "Votre Paiement a été annulé."
    return cart(request, message_error)


def mark_as_read(request):
    message_id = request.GET.get('message', 'None')
    type_message = request.GET.get('type', 'None')
    is_read = request.GET.get('is_read', 'unread')
    message_error = ""
    if request.user.is_authenticated:
        if message_id != "None" and type != "None":
            if type_message == 'student':
                selected_message = MessageToStudent.objects.filter(pk=message_id)
            else:
                selected_message = MessageToTeacher.objects.filter(pk=message_id)
            if selected_message.exists():
                selected_message = selected_message.first()
                if is_read == "unread":
                    selected_message.is_read = True
                else:
                    selected_message.is_read = False
                selected_message.save()
            else:
                message_error = "Ce message n'existe pas."
        else:
            message_error = "Données non valides."
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error,
        'is_read': is_read
    }
    return JsonResponse(data)


def course_rate(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    elif not request.method == "POST":
        return HttpResponseRedirect(reverse('eLearning:index'))
    else:
        id_course = request.POST.get("ratedCourse", "0")
        student = request.user.profil
        selected_course = get_object_or_404(Course, pk=id_course)
        comment = request.POST.get("commentRating", "")
        value = request.POST.get("valueRating", 0)
        Ratting.objects.create(student=student, course=selected_course, value=value, comment=comment)
        return HttpResponseRedirect(reverse('eLearning:course', kwargs={'id_course': id_course}))


def purchase(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    elif not request.method == "POST":
        return HttpResponseRedirect(reverse('eLearning:index'))
    else:
        id_course = request.POST.get("course", "0")
        student = request.user.profil
        selected_course = get_object_or_404(Course, pk=id_course)
        Formation.objects.get_or_create(student=student, course=selected_course)
        message = "Vous êtes inscrit au cours : <b>{}</b>".format(selected_course.name)
        send_mail(
            'No reply',
            message,
            'admin@socifly.com',
            [student.user.email, ],
            fail_silently=False,
            html_message=message,
        )
        return HttpResponseRedirect(reverse('eLearning:course', kwargs={'id_course': id_course}))


def apply_coupon(request):
    course_id = request.GET.get('course', 'None')
    coupon_value = request.GET.get('coupon', 'None')
    message_error = ""
    percentage = 0
    price = 0
    if course_id != "None" and coupon_value != "None":
        selected_course = Course.objects.filter(pk=course_id)
        if selected_course.exists():
            selected_course = selected_course.first()
            coupons = Coupon.objects.filter((Q(is_general=True) | (Q(is_general=False) & Q(course=selected_course))) & Q(value=coupon_value) & Q(used=False))
            if coupons.exists():
                percentage = coupons.first().percentage
                price = selected_course.price
            else:
                message_error = "Ce coupon est invalide ou déjà utilisé"
        else:
            message_error = "Ce cours n'existe pas."
    else:
        message_error = "Données non valides."

    data = {
        'message_error': message_error,
        'percentage': percentage,
        'price': price
    }
    return JsonResponse(data)


def apply_coupon_cart(request):
    coupon_value = request.GET.get('coupon', "None")
    coupon_values = request.GET.getlist('coupon_values', [])
    message_error = ""
    courses = []
    total = 0
    works = False
    if coupon_value != "None":
        user = request.user
        courses_result = Cart.objects.filter(user=user.profil)
        for c in courses_result:
            c = c.course
            coupon_first = Coupon.objects.filter((Q(is_general=True) | (Q(is_general=False) & Q(course=c))) & Q(value=coupon_value) & Q(used=False))
            if coupon_first.exists():
                coupon_values.append(coupon_value)
                works = True
            coupons = Coupon.objects.filter(
                (Q(is_general=True) | (Q(is_general=False) & Q(course=c))) & Q(value__in=coupon_values) & Q(
                    used=False)).order_by("-percentage")
            if coupons.exists() and not c.is_free:
                el = {'id': c.id}
                percentage = coupons.first().percentage
                el['percentage'] = percentage
                el['price'] = c.price - (c.price * percentage / 100)
                total += el['price']
                courses.append(el)
            else:
                sale = c.elearning_sale_set.filter(date_end__gte=timezone.now()).order_by('date_end')
                if sale.exists():
                    total += sale[0].new_price()
                else:
                    total += c.price
    else:
        message_error = "Données non valides."
    data = {
        'message_error': message_error,
        'total': total,
        'courses': courses,
        'works': works
    }
    return JsonResponse(data)


# Cart - Wish List
def add_to_wish(request):
    course_id = request.GET.get('course', "None")
    message_error = ""
    if request.user.is_authenticated:
        if course_id != "None":
            user = request.user
            wished_course = Course.objects.filter(pk=course_id)
            if wished_course.exists():
                if not WishList.objects.filter(user=user.profil, course=wished_course[0]).exists():
                    WishList.objects.create(user=user.profil, course=wished_course[0])
                    wished_course[0].add_like()
                else:
                    message_error = "Cours existe déjà dans votre liste des favoris."
            else:
                message_error = "Ce cours n'existe pas."
        else:
            message_error = "Données non valides."
    else:
        message_error = "Vous devez se connecter!."
    data = {
        'message_error': message_error,
    }
    return JsonResponse(data)


def remove_from_wish(request):
    if request.method == "POST":
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect(reverse('eLearning:index'))
        id_course = request.POST.get('course')
        wished_course = get_object_or_404(Course, pk=id_course)
        wish_object = get_object_or_404(WishList, user=user.profil, course=wished_course)
        wish_object.delete()
    return HttpResponseRedirect(reverse('eLearning:wish_list'))


def add_to_cart(request):
    course_id = request.GET.get('course', "None")
    message_error = ""
    if request.user.is_authenticated:
        if course_id != "None":
            user = request.user
            wished_course = Course.objects.filter(pk=course_id)
            if wished_course.exists():
                cart_objects = Cart.objects.filter(user=user.profil, course=wished_course.first())
                if not cart_objects.exists():
                    Cart.objects.create(user=user.profil, course=wished_course.first())
                else:
                    message_error = "Ce cours existe déjà dans votre panier."
            else:
                message_error = "Ce cours n'existe pas."
        else:
            message_error = "Données non valides."
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error
    }
    return JsonResponse(data)


def remove_from_cart(request, id_cart=None):
    if request.user.is_authenticated:
        if id_cart is not None:
            cart_object = Cart.objects.filter(pk=id_cart)
            if cart_object.exists():
                if cart_object.first().user == request.user.profil:
                    cart_object.delete()
        return HttpResponseRedirect(reverse('eLearning:cart'))
    else:
        return HttpResponseRedirect(reverse('eLearning:index'))


def unsubscribe(request, id_formation=None):
    if request.user.is_authenticated:
        if id_formation is not None:
            formation_object = Formation.objects.filter(pk=id_formation)
            if formation_object.exists():
                if formation_object.first().student == request.user.profil:
                    formation_object.delete()
        return HttpResponseRedirect(reverse('eLearning:student_dashboard'))
    else:
        return HttpResponseRedirect(reverse('eLearning:index'))


def remove_from_cart_ajax(request):
    message_error = ""
    id_cart = request.GET.get('cart', "None")
    if id_cart is None:
        message_error = "Données non valides."
    else:
        cart_object = Cart.objects.filter(pk=id_cart)
        if cart_object.exists():
            cart_object.delete()
        else:
            message_error = "Ce cours n'existe pas dans votre panier."
    data = {
        "message_error": message_error
    }
    return JsonResponse(data)


def add_progress(request):
    chapter_id = request.GET.get('chapter', "None")
    message_error = ""
    progress = None
    if request.user.is_authenticated:
        if chapter_id != "None":
            wished_chapter = Chapter.objects.filter(pk=chapter_id)
            if wished_chapter.exists():
                wished_chapter = wished_chapter.first()
                progress = Progress.objects.get_or_create(student=request.user.profil, chapter=wished_chapter)
                progress[0].date_add = timezone.now()
                progress[0].save()
                number_chapters = Chapter.objects.filter(part__course=wished_chapter.part.course).count()
                if number_chapters > 0:
                    number_chapters_seen = Progress.objects.filter(chapter__part__course=wished_chapter.part.course,
                                                                   student=request.user.profil).count()
                    progress = (number_chapters_seen * 100) / number_chapters
            else:
                message_error = "Ce chapitre n'existe pas."
        else:
            message_error = "Données non valides."
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error,
        'progress': str(progress).replace(',', '.')
    }
    return JsonResponse(data)


# teacher
def teacher_dashboard(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    if not request.user.profil.is_teacher:
        return HttpResponseRedirect(reverse('eLearning:index'))
    courses_filter = Course.objects.filter(teacher=request.user.profil, to_evaluate=False, active=True, approved=False)
    courses = []
    for c in courses_filter:
        row = {'c': c, 'number_chapters': Chapter.objects.filter(part__course=c).count()}
        courses.append(row)
    context = {
        'courses': courses
    }
    return render(request, 'dashboard-teacher/index.html', context)


def add_course(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    if not request.user.profil.is_teacher:
        return HttpResponseRedirect(reverse('eLearning:index'))
    form = PostCourseForm()
    message_error = None
    if request.method == 'POST':
        form = PostCourseForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            name = cd['name']
            description = cd['description']
            video_url = cd['video_url']
            is_free = cd['is_free']
            price = cd['price']
            duration = cd['duration']
            image = cd['image']
            language = cd['language']
            level = cd['level']
            has_certificate = cd['has_certificate']
            welcome_msg = cd['welcome_msg']
            congratulation_msg = cd['congratulation_msg']
            pk_category = request.POST.get('category', '0')
            selected_category = SubCategory.objects.filter(pk=pk_category)
            if price == 0 or price == "":
                is_free = True
            if selected_category.exists():
                crs = Course.objects.create(name=name, description=description, video_url=video_url, is_free=is_free,
                                            price=price, duration=duration, image=image, language=language, level=level,
                                            has_certificate=has_certificate, welcome_msg=welcome_msg,
                                            congratulation_msg=congratulation_msg,
                                            category=selected_category.first(), teacher=request.user.profil)
                return HttpResponseRedirect(reverse('eLearning:manage_course', kwargs={'id_course': crs.pk}))
            else:
                message_error = "Catégorie - veuillez choisir une sous-catégorie valide"
    context = {
        'form': form,
        'categories': Category.objects.all(),
        'message_error': message_error
    }
    return render(request, 'dashboard-teacher/add-course.html', context)


def dashboard_update_profile(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    if not request.user.profil.is_teacher:
        return HttpResponseRedirect(reverse('eLearning:index'))
    if request.method == "POST":
        form = UpdateTeacherProfil(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            first_name = cd['first_name']
            last_name = cd['last_name']
            email = cd['email']
            phone = cd['tel']
            photo_profil = cd['photo_profil']
            facebook = cd['facebook']
            youtube = cd['youtube']
            linkedin = cd['linkedin']
            twitter = cd['twitter']
            teacher_title = cd['title']
            biography = cd['biography']
            cv = cd['cv']
            user = request.user
            if first_name != '':
                user.first_name = first_name
            if last_name != '':
                user.last_name = last_name
            if email != '':
                user.email = email
            user.save()
            profil = user.profil
            if phone != '':
                profil.tel = phone
            if facebook != '':
                profil.facebook = facebook
            if youtube != '':
                profil.youtube = youtube
            if linkedin != '':
                profil.linkedin = linkedin
            if twitter != '':
                profil.twitter = twitter
            if teacher_title != '':
                profil.teacher_title = teacher_title
            if biography != '':
                profil.biography = biography
            if photo_profil is not None:
                img = Image.objects.create(image=photo_profil)
                profil.photo_profil = img
            if cv is not None:
                profil.cv = cv
            profil.request_teacher = True
            profil.save()
    else:
        form = UpdateTeacherProfil(initial={
            'biography': request.user.profil.biography,
            'last_name': request.user.last_name
        })
        form.fields['first_name'].widget.attrs['value'] = request.user.first_name
        form.fields['email'].widget.attrs['value'] = request.user.email
        form.fields['tel'].widget.attrs['value'] = request.user.profil.tel
        form.fields['facebook'].widget.attrs['value'] = request.user.profil.facebook
        form.fields['youtube'].widget.attrs['value'] = request.user.profil.youtube
        form.fields['twitter'].widget.attrs['value'] = request.user.profil.twitter
        form.fields['linkedin'].widget.attrs['value'] = request.user.profil.linkedin
        form.fields['title'].widget.attrs['value'] = request.user.profil.teacher_title
    context = {
        'form': form
    }
    return render(request, 'dashboard-teacher/teacher-profile.html', context)


def dashboard_courses(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    if not request.user.profil.is_teacher:
        return HttpResponseRedirect(reverse('eLearning:index'))
    courses = Course.objects.filter(teacher=request.user.profil, active=True)
    page = request.GET.get('page', 1)
    filter_by = request.GET.get('filter_by', 1)
    if filter_by == '2':
        courses = courses.filter(approved=True)
    if filter_by == '3':
        courses = courses.filter(to_evaluate=True, approved=False)
    if filter_by == '4':
        courses = courses.filter(refused=True, approved=False, to_evaluate=False)
    paginator = Paginator(courses, 10)
    try:
        courses_page = paginator.page(page)
    except PageNotAnInteger:
        courses_page = paginator.page(1)
    except EmptyPage:
        courses_page = paginator.page(paginator.num_pages)
    form_mail = SendMessageForm()
    number_messages = MailingCourse.objects.filter(course__teacher=request.user.profil,
                                                   date_add__month=timezone.now().month).count()
    context = {
        'courses': courses_page,
        'filter_by': filter_by,
        'form': form_mail,
        'number_messages_allowed': number_messages,
    }
    return render(request, 'dashboard-teacher/dashboard-courses.html', context)


def dashboard_revues(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    if not request.user.profil.is_teacher:
        return HttpResponseRedirect(reverse('eLearning:index'))
    reviews = Ratting.objects.filter(course__teacher=request.user.profil, course__active=True)
    page = request.GET.get('page', 1)
    course_list = reviews.values(pk=F('course__pk'), name=F('course__name')).distinct()
    filter_by = int(request.GET.get('filter_by', 0))
    if filter_by != 0:
        reviews = reviews.filter(course__pk=filter_by)

    order_by = request.GET.get('order_by', '1')
    if order_by == '1' or order_by == '2':
        reviews = reviews.order_by('date_add').reverse()
    if order_by == '3':
        reviews = reviews.order_by('date_add')
    if order_by == '4':
        reviews = reviews.order_by('value').reverse()
    if order_by == '5':
        reviews = reviews.order_by('value')
    if order_by == '6':
        reviews = reviews.order_by('course__name')
    if order_by == '7':
        reviews = reviews.order_by('course__name').reverse()

    paginator = Paginator(reviews, 10)
    try:
        reviews_page = paginator.page(page)
    except PageNotAnInteger:
        reviews_page = paginator.page(1)
    except EmptyPage:
        reviews_page = paginator.page(paginator.num_pages)

    context = {
        'reviews': reviews_page,
        'filter_by': filter_by,
        'order_by': order_by,
        'course_list': course_list
    }
    return render(request, 'dashboard-teacher/dashboard-reviews.html', context)


def dashboard_messages(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    if not request.user.profil.is_teacher:
        return HttpResponseRedirect(reverse('eLearning:index'))

    messages = MessageToTeacher.objects.filter(teacher=request.user.profil)

    page = request.GET.get('page', 1)
    filter_by = request.GET.get('filter_by', 1)
    order_by = request.GET.get('order_by', '1')
    filter_students = request.GET.get('filter_students', 1)

    if filter_by == '2':
        messages = messages.filter(is_read=False)
    if filter_by == '3':
        messages = messages.filter(is_read=True)

    students = Profil.objects.filter(formation__course__teacher=request.user.profil)
    if filter_students == '2':
        messages = messages.filter(student__in=students)
    if filter_students == '3':
        messages = messages.exclude(student__in=students)

    if order_by == '1' or order_by == '2':
        messages = messages.order_by('date_add').reverse()
    if order_by == '3':
        messages = messages.order_by('date_add')
    if order_by == '4':
        messages = messages.order_by('student__user__last_name', 'student__user__first_name')
    if order_by == '5':
        messages = messages.order_by('student__user__last_name', 'student__user__first_name').reverse()

    messages_list = []
    for message in messages:
        row = {'m': message}
        if message.student in students:
            row['is_student'] = True
        else:
            row['is_student'] = False
        messages_list.append(row)

    paginator = Paginator(messages_list, 10)
    try:
        messages_page = paginator.page(page)
    except PageNotAnInteger:
        messages_page = paginator.page(1)
    except EmptyPage:
        messages_page = paginator.page(paginator.num_pages)

    context = {
        'messages': messages_page,
        'order_by': order_by,
        'filter_by': filter_by,
        'filter_students': filter_students
    }
    return render(request, 'dashboard-teacher/dashboard-messages.html', context)


def dashboard_messages_reply(request, id_message):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    if not request.user.profil.is_teacher:
        return HttpResponseRedirect(reverse('eLearning:index'))
    selected_message = get_object_or_404(MessageToTeacher, pk=id_message)
    selected_message.is_read = True
    selected_message.save()

    form = ReplyMessageForm()
    if request.method == "POST":
        form = ReplyMessageForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            message = cd['message']
            MessageToStudent.objects.create(message=message, parent_message=selected_message)
            return HttpResponseRedirect(reverse('eLearning:dashboard_messages'))
    context = {
        'message': selected_message,
        'form': form
    }
    return render(request, 'dashboard-teacher/reply-message.html', context)


def manage_course(request, id_course, message_error="", message_success=""):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    if not request.user.profil.is_teacher:
        return HttpResponseRedirect(reverse('eLearning:index'))
    selected_course = get_object_or_404(Course, pk=id_course)
    if selected_course.teacher != request.user.profil:  # in cas he tries to manage another course
        return HttpResponseRedirect(reverse('eLearning:index'))
    form = AddPartForm(initial={
        'number': selected_course.elearning_part_set.count() + 1,
    })
    message_error_part = None
    if request.method == 'POST':
        return add_part(request, selected_course, message_error_part)
    context = {
        'course': selected_course,
        'form': form,
        'message_error_part': message_error_part,
        'message_error': message_error,
        'message_success': message_success,
        'form_quiz': AddQuizForm(),
        'form_question': AddQuestionForm()
    }
    return render(request, 'dashboard-teacher/manage-course.html', context)


def delete_course(request, id_course, page=1, filter_by=1):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    if not request.user.profil.is_teacher:
        return HttpResponseRedirect(reverse('eLearning:index'))
    selected_course = get_object_or_404(Course, pk=id_course)
    if selected_course.teacher != request.user.profil:
        return HttpResponseRedirect(reverse('eLearning:index'))
    selected_course.delete_course()
    if page == -1:
        return HttpResponseRedirect(reverse('eLearning:teacher_dashboard'))
    return HttpResponseRedirect(reverse('eLearning:dashboard_courses') + '?page={}&filter_by={}'.format(page,
                                                                                                        filter_by))


def delete_course_index(request, id_course):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eLearning:index'))
    if not request.user.profil.is_teacher:
        return HttpResponseRedirect(reverse('eLearning:index'))
    selected_course = get_object_or_404(Course, pk=id_course)
    if selected_course.teacher != request.user.profil:
        return HttpResponseRedirect(reverse('eLearning:index'))
    selected_course.delete_course()
    return HttpResponseRedirect(reverse('eLearning:teacher_dashboard'))


def teacher_send_mail(request):
    course_id = request.POST.get('course', "None")
    object_mail = request.POST.get('object', '')
    message = request.POST.get('message', '')
    message_error = ""
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_course = selected_course.first()
                    number_messages = MailingCourse.objects.filter(course__teacher=selected_course.teacher,
                                                                   date_add__month=timezone.now().month).count()
                    if number_messages < 5:
                        emails = list(selected_course.elearning_formation_set.values_list('student__user__email', flat=True))
                        send_mail(
                            object_mail,
                            message,
                            'admin@socifly.com',
                            emails,
                            fail_silently=False,
                            html_message=message,
                        )
                        MailingCourse.objects.create(object=object_mail, message=message, course=selected_course)
                    else:
                        message_error = "Vous avez déjà envoyé 5 messages ce mois."
                else:
                    message_error = "Ce cours n'existe pas."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error
    }
    return JsonResponse(data)


def message_to_teacher(request):
    teacher_id = request.GET.get('teacher', "None")
    object_mail = request.GET.get('object', '')
    message = request.GET.get('message', '')
    message_error = ""
    if request.user.is_authenticated:
        if teacher_id != "None" or object_mail == '' or message == '':
            selected_teacher = Profil.objects.filter(pk=teacher_id)
            if selected_teacher.exists():
                selected_teacher = selected_teacher.first()
                MessageToTeacher.objects.create(teacher=selected_teacher, student=request.user.profil, message=message,
                                                object=object_mail)
                '''send_mail(
                    object_mail,
                    message,
                    'admin@socifly.com',
                    [selected_teacher.user.email,],
                    fail_silently=False,
                    html_message=message,
                )'''
            else:
                message_error = "Ce cours n'existe pas"
        else:
            message_error = "Données non valides."
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error
    }
    return JsonResponse(data)


def update_price(request):
    course_id = request.GET.get('course', "None")
    price = request.GET.get('price', '')
    message_error = ""
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_course = selected_course.first()
                    if price == '':
                        selected_course.price = 0
                        selected_course.is_free = True
                        selected_course.save()
                    else:
                        try:
                            price = float(price)
                            if price == 0:
                                selected_course.price = 0
                                selected_course.is_free = True
                                selected_course.save()
                            else:
                                selected_course.price = float(price)
                                selected_course.is_free = False
                                selected_course.save()
                        except ValueError:
                            message_error = "Prix non valide."
                else:
                    message_error = "Ce cours n'existe pas."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter."

    data = {
        'message_error': message_error,
    }
    return JsonResponse(data)


def update_url_part(request):
    course_id = request.GET.get('course', "None")
    part_id = request.GET.get('part', "None")
    url = request.GET.get('url', '')
    message_error = ""
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None" and part_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_course = selected_course.first()
                    selected_part = Part.objects.filter(pk=part_id, course=selected_course)
                    if selected_part.exists():
                        selected_part = selected_part.first()
                        selected_part.attached_file_url = url
                        selected_part.save()
                    else:
                        message_error = "Cette Section n'existe pas."
                else:
                    message_error = "Ce cours n'existe pas."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"
    data = {
        'message_error': message_error,
    }
    return JsonResponse(data)


def update_file_part(request):
    course_id = request.POST.get('course', "None")
    part_id = request.POST.get('part', "None")
    attached_file = request.FILES.get('attached_file', None)
    message_error = ""
    url_file = ""
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None" and part_id != "None":
                if attached_file is not None:
                    selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                    if selected_course.exists():
                        selected_course = selected_course.first()
                        selected_part = Part.objects.filter(pk=part_id, course=selected_course)
                        if selected_part.exists():
                            selected_part = selected_part.first()
                            selected_part.attached_file = attached_file
                            selected_part.save()
                            url_file = selected_part.attached_file.url
                        else:
                            message_error = "Cette Section n'existe pas."
                    else:
                        message_error = "Ce cours n'existe pas."
                else:
                    message_error = "Fichier non valide."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error,
        'url_file': url_file,
        'part_id': part_id
    }
    return JsonResponse(data)


def add_prerequisite_postskill(request):
    course_id = request.POST.get('course', "None")
    values_prerequisite = request.POST.getlist('values_prerequisite', [])
    values_postskill = request.POST.getlist('values_postskill', [])
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_course = selected_course.first()
                    for value in values_prerequisite:
                        Prerequisites.objects.create(value=value, course=selected_course)
                    for value in values_postskill:
                        PostSkills.objects.create(value=value, course=selected_course)
    return HttpResponseRedirect(reverse('eLearning:manage_course', kwargs={'id_course': course_id}))


def add_coupon(request):
    course_id = request.POST.get('course', "None")
    values_coupon = request.POST.getlist('values_coupon', [])
    is_multiple = request.POST.getlist('is_multiple', [])
    percentage_coupon = list(map(int, request.POST.getlist('percentage_coupon', [])))
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_course = selected_course.first()
                    for i, value in enumerate(values_coupon):
                        if 0 < percentage_coupon[i] <= 100:
                            is_multiple_value = False
                            if is_multiple[i] == '2':
                                is_multiple_value = True
                            Coupon.objects.create(value=value, percentage=percentage_coupon[i], is_multiple=is_multiple_value, course=selected_course)
    return HttpResponseRedirect(reverse('eLearning:manage_course', kwargs={'id_course': course_id}))


def add_part(request, selected_course, message_error_part):
    form = AddPartForm(request.POST, request.FILES)
    if form.is_valid():
        cd = form.cleaned_data
        number = cd['number']
        name = cd['name']
        is_free = cd['is_free']
        selected_part = Part.objects.filter(course=selected_course).filter(Q(number=number) | Q(name=name))
        if not selected_part.exists():
            part = Part(course=selected_course, number=number, name=name, is_free=is_free)
            part.save()
            form = AddPartForm(initial={
                'number': part.number + 1,
            })
        else:
            message_error_part = "Section - Cette section existe déjà."
    context = {
        'course': selected_course,
        'form': form,
        'message_error_part': message_error_part
    }
    return render(request, 'dashboard-teacher/manage-course.html', context)


def add_chapter(request):
    course_id = request.POST.get('course', 'None')
    part_id = request.POST.get('part', 'None')
    number = request.POST.get('number', '')
    name = request.POST.get('name', '')
    duration = request.POST.get('duration', '')
    video_url = request.POST.get('video_url', None)
    video_file = request.FILES.get('video_file', None)
    message_error = ""
    chapter = None
    selected_course = None
    if (video_file and video_url) or (video_file is None and video_url is None):
        message_error = "Vous devez choisir entre l'url du vidéo ou l'importer."
    else:
        if request.user.is_authenticated:
            if request.user.profil.is_teacher:
                if course_id != "None" and part_id != "None":
                    selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                    if selected_course.exists():
                        selected_course = selected_course.first()
                        selected_part = Part.objects.filter(pk=part_id, course=selected_course)
                        if selected_part.exists():
                            selected_part = selected_part.first()
                            chapter = Chapter.objects.create(name=name, number=number, video_url=video_url, duration=duration, video_file=video_file, part=selected_part)
                        else:
                            message_error = "Ce cours n'existe pas."
                    else:
                        message_error = "Ce cours n'existe pas."
                else:
                    message_error = "Données non valides."
            else:
                message_error = "Vous devez être formateur."
        else:
            message_error = "Vous devez se connecter!"
    data = {
        'message_error': message_error,
    }
    if message_error == "":
        data["url"] = reverse("eLearning:delete_chapter")
        data["course_id"] = selected_course.pk
        data["part_id"] = chapter.part.pk
        data["chapter_id"] = chapter.pk
        data["number"] = chapter.number
        data["name"] = chapter.name
        data["duration"] = chapter.duration
        if video_file:
            data["video_file"] = chapter.video_file.url
        else:
            data["video_file"] = ""
        if video_url:
            data["video_url"] = (video_url[:35] + '..') if len(video_url) > 35 else video_url
        else:
            data["video_url"] = ""
    return JsonResponse(data)


def add_quiz(request):
    course_id = request.POST.get('course', 'None')
    part_id = request.POST.get('part', 'None')
    title = request.POST.get('title', '')
    description = request.POST.get('description', '')
    message_error = ""
    quiz_ = None
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None" and part_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_course = selected_course.first()
                    selected_part = Part.objects.filter(pk=part_id, course=selected_course)
                    if selected_part.exists():
                        selected_part = selected_part.first()
                        if not Exam.objects.filter(part=selected_part).exists():
                            quiz_ = Exam.objects.create(title=title, description=description, part=selected_part)
                        else:
                            message_error = "Cette section contient déjà un quiz."
                    else:
                        message_error = "Ce cours n'existe pas."
                else:
                    message_error = "Ce cours n'existe pas."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"
    data = {
        'message_error': message_error,
    }
    if message_error == "":
        data["url"] = reverse("eLearning:delete_quiz")
        data["quiz_id"] = quiz_.pk
        data["quiz_title"] = title
        data["part_id"] = quiz_.part_id
        data["part_name"] = quiz_.part.name
        data["course_id"] = quiz_.part.course_id
    return JsonResponse(data)


def add_question(request):
    course_id = request.POST.get('course', 'None')
    quiz_id = request.POST.get('quiz', 'None')
    text = request.POST.get('text', '')
    explanation = request.POST.get('explanation', '')
    is_multiple = request.POST.get('is_multiple', False)
    message_error = ""
    question = None
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None" and quiz_id != "None":
                if text != "":
                    selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                    if selected_course.exists():
                        selected_course = selected_course.first()
                        selected_quiz = Exam.objects.filter(pk=quiz_id, part__course=selected_course)
                        if selected_quiz.exists():
                            selected_quiz = selected_quiz.first()
                            if is_multiple == "on":
                                is_multiple = True
                            else:
                                is_multiple = False
                            question = Question.objects.create(text=text, explanation=explanation, exam=selected_quiz, is_multiple=is_multiple)
                        else:
                            message_error = "Cet exam n'existe pas."
                    else:
                        message_error = "Ce cours n'existe pas."
                else:
                    message_error = "Le texte est obligatoire."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"
    data = {
        'message_error': message_error,
    }
    if message_error == "":
        data["url"] = reverse("eLearning:delete_question")
        data["question_id"] = question.pk
        data["course_id"] = course_id
        data["question_number"] = Question.objects.filter(exam_id=question.exam_id).count()
        data["exam_id"] = question.exam_id
        data["question_text"] = text

    return JsonResponse(data)


def add_choice(request):
    course_id = request.POST.get('course', 'None')
    question_id = request.POST.get('question', 'None')
    value = request.POST.get('value', '')
    is_correct = request.POST.get('is_correct', False)
    message_error = ""
    choice = None
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None" and question_id != "None":
                if value != "":
                    selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                    if selected_course.exists():
                        selected_course = selected_course.first()
                        selected_question = Question.objects.filter(pk=question_id, exam__part__course=selected_course)
                        if selected_question.exists():
                            selected_question = selected_question.first()
                            if is_correct == "on":
                                is_correct = True
                            else:
                                is_correct = False
                            choice = Choice.objects.create(value=value, is_correct=is_correct, question=selected_question)
                        else:
                            message_error = "Ce cours n'existe pas."
                    else:
                        message_error = "Ce cours n'existe pas."
                else:
                    message_error = "La Valeur est obligatoire."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"
    data = {
        'message_error': message_error,
    }
    if message_error == "":
        data["url"] = reverse("eLearning:delete_choice")
        data["question_id"] = question_id
        data["choice_id"] = choice.pk
        data["is_correct"] = is_correct
        data["course_id"] = course_id
    return JsonResponse(data)


def delete_prerequisite(request):
    course_id = request.GET.get('course', 'None')
    prerequisite_id = request.GET.get('prerequisite', 'None')
    message_error = ""
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None" and prerequisite_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_prerequisite = Prerequisites.objects.filter(pk=prerequisite_id, course_id=course_id)
                    if selected_prerequisite.exists():
                        selected_prerequisite.first().delete()
                    else:
                        message_error = "Ce prérequis n'existe pas."
                else:
                    message_error = "Ce cours n'existe pas."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error
    }
    return JsonResponse(data)


def delete_postskill(request):
    course_id = request.GET.get('course', 'None')
    postskill_id = request.GET.get('postskill', 'None')
    message_error = ""
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None" and postskill_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_postskill = PostSkills.objects.filter(pk=postskill_id, course_id=course_id)
                    if selected_postskill.exists():
                        selected_postskill.first().delete()
                    else:
                        message_error = "Ce post skill n'existe pas."
                else:
                    message_error = "Ce cours n'existe pas."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error
    }
    return JsonResponse(data)


def delete_coupon(request):
    course_id = request.GET.get('course', 'None')
    coupon_id = request.GET.get('coupon', 'None')
    message_error = ""
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None" and coupon_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_coupon = Coupon.objects.filter(pk=coupon_id, course_id=course_id)
                    if selected_coupon.exists():
                        selected_coupon.first().delete()
                    else:
                        message_error = "Ce coupon n'existe pas."
                else:
                    message_error = "Ce cours n'existe pas."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error
    }
    return JsonResponse(data)


def delete_part(request):
    course_id = request.GET.get('course', 'None')
    part_id = request.GET.get('part', 'None')
    message_error = ""
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None" and part_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_part = Part.objects.filter(pk=part_id, course_id=course_id)
                    if selected_part.exists():
                        selected_part.first().delete()
                    else:
                        message_error = "Cette section n'existe pas."
                else:
                    message_error = "Ce cours n'existe pas."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error
    }
    return JsonResponse(data)


def delete_quiz(request):
    course_id = request.GET.get('course', 'None')
    part_id = request.GET.get('part', 'None')
    quiz_id = request.GET.get('quiz', 'None')
    message_error = ""
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None" and part_id != "None" and quiz_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_quiz = Exam.objects.filter(pk=quiz_id, part_id=part_id, part__course_id=course_id)
                    if selected_quiz.exists():
                        selected_quiz.first().delete()
                    else:
                        message_error = "Ce quiz n'existe pas."
                else:
                    message_error = "Ce cours n'existe pas."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error
    }
    return JsonResponse(data)


def delete_chapter(request):
    course_id = request.GET.get('course', 'None')
    chapter_id = request.GET.get('chapter', 'None')
    message_error = ""
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None" and chapter_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_chapter = Chapter.objects.filter(pk=chapter_id, part__course_id=course_id)
                    if selected_chapter.exists():
                        selected_chapter.first().delete()
                    else:
                        message_error = "Cette section n'existe pas."
                else:
                    message_error = "Ce cours n'existe pas."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error
    }
    return JsonResponse(data)


def delete_question(request):
    course_id = request.GET.get('course', 'None')
    question_id = request.GET.get('question', 'None')
    message_error = ""
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None" and question_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_question = Question.objects.filter(pk=question_id, exam__part__course_id=course_id)
                    if selected_question.exists():
                        selected_question.first().delete()
                    else:
                        message_error = "Cette question n'existe pas."
                else:
                    message_error = "Ce cours n'existe pas."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error
    }
    return JsonResponse(data)


def delete_choice(request):
    course_id = request.GET.get('course', 'None')
    choice_id = request.GET.get('choice', 'None')
    message_error = ""
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None" and choice_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_choice = Choice.objects.filter(pk=choice_id, question__exam__part__course_id=course_id)
                    if selected_choice.exists():
                        selected_choice.first().delete()
                    else:
                        message_error = "Ce choix n'existe pas."
                else:
                    message_error = "Ce cours n'existe pas."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"

    data = {
        'message_error': message_error
    }
    return JsonResponse(data)


def send_to_evaluate(request):
    course_id = request.GET.get('course', 'None')
    message_error = None
    if request.user.is_authenticated:
        if request.user.profil.is_teacher:
            if course_id != "None":
                selected_course = Course.objects.filter(pk=course_id, teacher=request.user.profil)
                if selected_course.exists():
                    selected_course.first().evaluate()
                else:
                    message_error = "Ce cours n'existe pas."
            else:
                message_error = "Données non valides."
        else:
            message_error = "Vous devez être formateur."
    else:
        message_error = "Vous devez se connecter!"
    if message_error:
        return manage_course(request, course_id, message_error)
    # return HttpResponseRedirect(reverse('eLearning:course', kwargs={'id_course': course_id}))
    return manage_course(request, course_id, "", "Votre cours a été envoyé pour s'évaluer.")


def course_share(request):
    pk = request.GET.get("id", None)

    try:
        pk = int(pk)
    except Exception:
        raise Exception()

    selected_course = get_object_or_404(Course, id=pk)
    selected_course.add_share()
    response = {}
    return JsonResponse(response, safe=False)
