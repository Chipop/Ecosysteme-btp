from django.contrib import admin
from .models import *

# Register your models here.

admin.site.site_header = "ESPR Administration"
admin.site.site_title = "ESPR Administration"

admin.site.register(Profil)
admin.site.register(Entreprise)
admin.site.register(Image)
admin.site.register(Contact)
admin.site.register(NewsLetterMails)
