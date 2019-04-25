
from django.core import mail
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from dashboard.models import Parameters
from SocialNetworkJob import settings

def send_mail(subject, message, from_email, recipient_list,
              fail_silently=False, auth_user=None, auth_password=None,
              connection=None, html_message=None):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.

    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    p = Parameters.get_object()

    connection = connection or get_connection(
        username=p.email_host_user,
        password=p.email_host_password,
        fail_silently=fail_silently,
    )
    mail = EmailMultiAlternatives(subject, message, from_email, recipient_list, connection=connection)
    if html_message:
        mail.attach_alternative(html_message, 'text/html')

    return mail.send()


def get_custom_connection():
    p = Parameters.get_object()
    if p.email_host_user == "" and p.email_host_password == "":
        p.email_host_user = settings.EMAIL_HOST_USER
        p.email_host_password = settings.EMAIL_HOST_PASSWORD
        p.save()
        if p.email_host_user == "" and p.email_host_password == "":
            raise Exception("Error 44 : Un problème de configuration email est survenu.")
    return get_connection(host=p.email_host,
                            port=p.email_port,
                            username=p.email_host_user,
                            password=p.email_host_password,
                            )
