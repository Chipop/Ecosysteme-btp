from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from .models import Profil

"""""""""""
@receiver(post_delete, sender=Profil)
def post_delete_user(sender, instance, *args, **kwargs):
    print("hhe")
    if instance.user: # just in case user is not specified
        instance.user.delete()
        print("hey dj")
"""""""""""

