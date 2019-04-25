from datetime import datetime

from django.db.models import Count

from ao.models import AO, AOSaves, PSaves, Keyword


def global_var(request):

    ao_profile = None
    ao_count = 0
    save_count = 0
    if request.user.is_authenticated:
        if request.user.profil is not None:
            ao_profile = request.user.profil
            ao_count = AO.objects.filter(user=ao_profile).count()
            save_count = AOSaves.objects.filter(user=ao_profile).count()
            save_count += PSaves.objects.filter(user=ao_profile).count()

    popular_aos = AO.objects.all().filter(date_limit__gte=datetime.now()).order_by('-views')[:6]
    top_keywords_ao = Keyword.objects.all().annotate(count_p=Count('project')).order_by('-count_p', 'name')[:13]

    context = {
        'ao_profile': ao_profile,
        'ao_count': ao_count,
        'save_count': save_count,
        'popular_aos': popular_aos,
        'top_keywords_ao': top_keywords_ao
    }

    return context
