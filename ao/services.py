from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


from django.core import mail

from ao.models import Contact
from main_app.SendMailBackend import get_custom_connection


def send_email(contact_id, type_):
    contact = Contact.objects.get(id=contact_id)
    body = get_template('ao/email/contact.html')
    subject = 'Nouvelle offre envoyé à prepos de votre ' + type_
    from_email = contact.company.mail
    context = {
        'contact': contact,
        'type': type_
    }
    html_content = body.render(context)
    msg = EmailMultiAlternatives(subject, '', from_email, [],connection=get_custom_connection())
    if type_ == 'appel d\'offre':
        msg.to.append(contact.ao.contact_mail)
    else:
        msg.to.append(contact.project.ao.contact_mail)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_multiple_mails(emails_addresses,sujet,message,request,object_,type_,company=None):  #  Object_ = Soit AO Soit Projet, Type  = 'ao' or 'project'
    connection = get_custom_connection()  # Use default email connection
    print(emails_addresses)
    # Manually open the connection
    connection.open()

    emails_list = []

    body = get_template('ao/email/contact_changed_announce.html')

    context = {
        'object_':object_,
        'company': company,
        'type_':type_,
        'message': message,
        'request':request
    }

    contenu_mail = body.render(context)

    for email_address in emails_addresses:
        email_to_send = EmailMultiAlternatives(
            sujet, # Subject
            contenu_mail, # Html content
            'Ecosysteme-BTP@gmail.com', #From Email
            [email_address, ], # To
        )
        email_to_send.attach_alternative(contenu_mail, "text/html")
        emails_list.append(email_to_send)

    # Send all emails in a single call -
    connection.send_messages(emails_list)
    # The connection was already open so send_messages() doesn't close it.
    # We need to manually close the connection.
    connection.close()



"""""""""
#Code pour envoie d'emails multiple, By Chipop
def send_multiple_mails(emails_addresses,sujet):
    connection = mail.get_connection()  # Use default email connection

    # Manually open the connection
    connection.open()

    emails_list = []

    body = get_template('ao/email/contact_changed_announce.html')

    context = {
        'contact': contact,
        'type': type_
    }

    contenu_mail = body.render(context)

    for email_address in emails_addresses:
        email_to_send = EmailMultiAlternatives(
            sujet, # Subject
            contenu_mail, # Html content
            'Ecosysteme-BTP@gmail.com', #From Email
            [email_address, ], # To
        )
        email_to_send.attach_alternative(contenu_mail, "text/html")
        emails_list.append(email_to_send)

    # Send all emails in a single call -
    connection.send_messages(emails_list)
    # The connection was already open so send_messages() doesn't close it.
    # We need to manually close the connection.
    connection.close()

"""""""""