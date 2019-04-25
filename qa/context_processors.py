from django.db.models import Count

from qa.models import Tag, Question, Category


def global_var(request):

    top_tag_qa = Tag.objects.all().annotate(count_q=Count('question')).order_by('-count_q')[:11]
    top_questions_qa = Question.objects.all().annotate(answers_count=Count('answer')).order_by("-views_number")[:5]

    autocomplete_strings_qa_1 = Tag.objects.all().values_list('title', flat=True)
    autocomplete_strings_qa_2 = Category.objects.all().exclude(title='Toutes les catégories')\
        .values_list('title', flat=True)

    qa_profile_id = None
    qa_profile_pro = None
    if request.user.is_authenticated:
        qa_profile_id = request.user.profil.id
        if request.user.profil.is_professional:
            qa_profile_pro = True

    context = {
        'top_tag_qa': top_tag_qa,
        'top_questions_qa': top_questions_qa,
        'autocomplete_strings_qa_1': autocomplete_strings_qa_1,
        'autocomplete_strings_qa_2': autocomplete_strings_qa_2,
        'qa_profile_id': qa_profile_id,
        'qa_profile_pro': qa_profile_pro
    }

    return context
