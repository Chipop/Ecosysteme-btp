import datetime

from django.db.models import Max
from django.shortcuts import get_object_or_404

from SocialMedia.models import *
from main_app.models import *
from SocialNetworkJob import settings


def global_var(request):

    context = {
        'entreprises': PageEntreprise.objects.all(),
        'grs': Groupe.objects.all()
    }

    context['PUSHER_INSTANCE_LOCATOR'] = settings.PUSHER_INSTANCE_LOCATOR

    return context
