from django.conf import settings
from dashboard.models import Parameters

def global_settings(request):
    # return any necessary values
    p = Parameters.get_object()
    return {
        'GOOGLE_ANALYTICS_ID': settings.GOOGLE_ANALYTICS,
        'website_title' : p.titre_site
    }
