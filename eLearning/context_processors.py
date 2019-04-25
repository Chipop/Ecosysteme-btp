from .models import *
from django.db.models import Avg, F, Count, Q


def global_var(request):
    # Footer Variables
    courses_pop = Formation.objects.all().values('course__id').annotate(number=Count('id'), c=F('course')).order_by('number').reverse()[:6]
    for course in courses_pop:
        course['c'] = Course.objects.get(pk=course['course__id'])

    cat_pop = Formation.objects.all().values('course__category__category__id').annotate(number=Count('id'), c=F('course__category__category'),
                    number_courses=Count('course__id')).order_by('number').reverse()[:11]
    for cat in cat_pop:
        cat['c'] = Category.objects.get(pk=cat['course__category__category__id'])

    number_messages = None
    messages_base = None
    if request.user.is_authenticated:
        if request.user.profil is not None:
            if request.user.profil.is_teacher:
                number_messages = MessageToTeacher.objects.filter(teacher=request.user.profil, is_read=False).count()
                messages_base = MessageToTeacher.objects.filter(teacher=request.user.profil, is_read=False).order_by('date_add').reverse()[:3]
    context = {
        'number_messages': number_messages,
        'messages_base': messages_base,
        'footer_course': courses_pop,
        'footer_cats': cat_pop,
    }
    return context
