import os
from oauth2client.service_account import ServiceAccountCredentials
from .models import Admin
from ecommerce.models import Shop
from main_app.models import Contact

# The scope for the OAuth2 request.
SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'

# The location of the key file with the key data.

module_dir = os.path.dirname(__file__)  # get current directory
GOOGLE_KEY_FILEPATH = os.path.join(module_dir, 'google_analytics_private_key.json')


# Defines a method to get an access token from the ServiceAccount object.
def get_access_token():
    return ServiceAccountCredentials.from_json_keyfile_name(
        GOOGLE_KEY_FILEPATH, SCOPE).get_access_token().access_token


# Global vars for context processors
def global_settings(request):
    # return any necessary values

    id_admin = request.session.get('id_admin', None)

    #print(request.path)
    #print("/dashboard/" in request.path)

    context = {}

    context['nb_demandes_exposants'] = Shop.objects.filter(approved=False).count()
    context['nb_messages_contact_non_lu'] = Contact.objects.filter(lu=False).count()
    context['messages_contact_non_lu'] = Contact.objects.filter(lu=False)[:3]

    if request.path == "/dashboard/" or "/general_view/" in request.path  or "/dashboard/marketplace/shop/" in  request.path  :
        context['ACCESS_TOKEN_FROM_GOOGLE_SERVICE_ACCOUNT'] = get_access_token()
        #print("dkhl")

    if request.session.get('id_admin', None) is not None:
        context['admin'] = Admin.objects.get(id=id_admin)

    return context
