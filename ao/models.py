import os
from datetime import datetime
from django.db import models
from django.urls import reverse

from main_app.models import Profil

from django.utils import timezone



#Profil Entreprise
class Company(models.Model):
    types = (('Petite entreprise', 'Petite entreprise'), ('Grande entreprise', 'Grande entreprise'),
             ('Très petite entreprise', 'Très petite entreprise'), ('Moyenne entreprise', 'Moyenne entreprise'))
    sectors = (('Publique', 'Publique'), ('Prive', 'Privé'))
    name = models.CharField(max_length=50)
    activity = models.CharField(max_length=255)
    capital = models.DecimalField(decimal_places=2, max_digits=20, null=True)
    country = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=50, null=True)
    codePostal = models.IntegerField(null=True)
    telephone = models.CharField(null=True, max_length=30)
    fax = models.CharField(max_length=20, null=True)
    mail = models.EmailField()
    trade_registry = models.CharField(max_length=100, null=True)
    logo = models.ImageField(null=True)
    description = models.TextField(null=True)
    facebook = models.URLField(max_length=50, default='#', blank=True)
    linkedIn = models.URLField(max_length=50, default='#', blank=True)
    twitter = models.URLField(max_length=50, default='#', blank=True)
    github = models.URLField(max_length=50, default='#', blank=True)
    youtube = models.URLField(max_length=50, default='#', blank=True)

    def __str__(self):
        return self.name

    def aos(self):
        user = AOUser.objects.get(company=self).user
        return user.ao_set.all().order_by('-views')[:5]

    def get_appels_offres(self):
        user = AOUser.objects.get(company=self).user
        return user.ao_set.all()

    def get_lots(self):
        lots = Project.objects.filter(ao__in=self.get_appels_offres())
        return lots

    def aouser(self):
        user = AOUser.objects.get(company=self).user
        return user

    def reviews(self):
        return self.review_set.all().order_by('-creation_date')

# Chaque compagnie a plusieurs reviews (1 to M )
class Review(models.Model):
    full_name = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    content = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Profil, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

#Comment connaitre l'utilisateur qui a le profil entreprise
class AOUser(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.user.first_name.capitalize() + ' ' + self.user.user.last_name.upper()

    @staticmethod
    def user_ids():
        ids = []
        for user in AOUser.objects.all():
            ids.append(user.id)
        return ids

    @staticmethod
    def user_ids_not():
        ids = []
        for user in Profil.objects.all():
            if user.id not in AOUser.user_ids():
                ids.append(user.id)
        return ids


class City(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(null=True)
    description = models.TextField(null=True)

    def __str__(self):
        return self.name

    def count(self):
        return self.project_set.count()

    def aos(self):
        ao_c = []
        for project in self.project_set.all():
            ao_c.append(project.ao)
        return list(set(ao_c))

    def aos_count(self):
        count = 0
        for _ in self.aos():
            count += 1
        return count

    def budget(self):
        budget = 0
        for project in self.project_set.all():
            budget += project.budget
        return budget

    def avg_budget(self):
        return self.budget() / self.project_set.all().count()


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    icon = models.CharField(max_length=60)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def add_view(self):
        self.views += 1
        self.save()

    def count_ao(self):
        return self.ao_set.all().count()

    def subs(self):
        subs = ""
        i = 0
        for s in self.subcategory_set.all():
            i += 1
            if i < 4:
                subs += s.name
            if i < 3:
                subs += ', '
        if self.subcategory_set.all().count() > 2:
            subs += ' et plus'
        return subs


class SubCategory(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def add_view(self):
        self.views += 1
        self.save()

    def count_views(self):
        c = 0
        for p in self.project_set.all():
            c += p.views
        return c

# Dans class Project (M2M) But : Recherche grace aux keywords
class Keyword(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

# Fichier pour Offer (FK) et AO (M2M)
class File(models.Model):
    file = models.FileField()
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

    def name(self):
        filename, file_extension = os.path.splitext(self.file.name)
        return filename

    def extension(self):
        filename, file_extension = os.path.splitext(self.file.name)
        return file_extension[1:]

# Fichier pour le lot : Relation M2M Chez la classe Projet ( lot )
class FileProject(models.Model):
    file = models.FileField()
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

    def name(self):
        filename, file_extension = os.path.splitext(self.file.name)
        return filename

    def extension(self):
        filename, file_extension = os.path.splitext(self.file.name)
        return file_extension[1:]

# Appel d'offre
class AO(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    date_limit = models.DateTimeField()
    time_limit = models.IntegerField(null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    contact_mail = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    views = models.IntegerField(default=0)
    files = models.ManyToManyField(File)
    cloturee = models.BooleanField(default=False)

    blacklisted_users = models.ManyToManyField(Profil,related_name="blacklisted_users_ao")
    blacklisted_companies = models.ManyToManyField(Company,related_name="blacklisted_companies_ao")

    downloaded_piecejointe_users = models.ManyToManyField(Profil,related_name="downloaded_piecejointe_users_ao")
    downloaded_piecejointe_companies = models.ManyToManyField(Company,related_name="downloaded_piecejointe_companies_ao")

    def __str__(self):
        return self.title

    def full_user_name(self):
        return self.user.user.first_name.capitalize() + ' ' + self.user.user.last_name.upper()

    def company(self):
        if AOUser.objects.filter(user=self.user).count() > 0:
            return AOUser.objects.get(user=self.user).company.name
        return self.full_user_name()

    def get_company(self):
        if AOUser.objects.filter(user=self.user).count() > 0:
            return AOUser.objects.get(user=self.user).company
        return  None

    def get_contact_mail(self):
        if AOUser.objects.filter(user=self.user).count() > 0:
            return AOUser.objects.get(user=self.user).company.mail
        return  self.user.user.email

    def get_interested_mails(self):
        emails = []
        for  company in self.downloaded_piecejointe_companies.all():
            emails.append(company.mail)
        for profil in self.downloaded_piecejointe_users.all():
            emails.append(profil.user.email)
        for devis in self.quotation_set.all():
            emails.append(devis.company.mail)
        for contact in self.contact_set.all():
            emails.append(contact.company.mail)
        return remove_duplicates(emails)

    def type_user(self):
        if AOUser.objects.filter(user=self.user).count() > 0:
            return 'company'
        return 'particular'

    def cities(self):
        city = ''
        for project in self.project_set.all():
            if project == self.project_set.all().last():
                for c in project.city.all():
                    if c.name not in city:
                        if c == project.city.all().last():
                            city += c.name.capitalize()
                        else:
                            city += c.name.capitalize() + ' - '
            else:
                for c in project.city.all():
                    if c.name not in city:
                        city += c.name.capitalize() + ' - '
        return city

    def budget(self):
        b = 0
        for project in Project.objects.filter(ao=self):
            b += project.budget
        return str(b).split(',')[0]

    def days_left(self):
        naive = self.date_limit.replace(tzinfo=None)
        date_d = naive - datetime.now()
        seconds = date_d.seconds
        hours = seconds // 3600
        return str(date_d.days) + ' Jours, {:02} Heures restants'.format(int(hours))

    def simple_date_limit(self):
        try:
            return self.date_limit.strftime('%Y-%m-%dT%H:%M')
        except AttributeError:
            return self.date_limit

    def image(self):
        if AOUser.objects.filter(user=self.user).count() > 0:
            if AOUser.objects.get(user=self.user).company.logo:
                return AOUser.objects.get(user=self.user).company.logo.url
            else:
                return None
        elif self.user.photo_profil is not None:
            return self.user.photo_profil.image.url
        else:
            return None

    def add_view(self):
        self.views += 1
        self.save()

    def related_ao(self):
        return AO.objects.filter(category=self.category).exclude(id=self.id).order_by('-creation_date')[:4]

    def get_etat(self):
        if self.cloturee:
            return "Cloturée"
        elif self.date_limit < timezone.now():
            return "Archivée"
        else:
            return "En cours"


    class Meta:
        verbose_name_plural = 'Appels  d\'offres'
        verbose_name = "Appel d'offre"

    def tracking_get_admin_url(self):
        return reverse('dashboard:ao_appel_offre',kwargs={'id':self.id})

    def tracking_get_absolute_url(self):
        return reverse('ao:ao', kwargs={'id_ao':self.id})

    def tracking_get_description(self):
        return self.title

#lot
class Project(models.Model):
    ao = models.ForeignKey(AO, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    categories = models.ManyToManyField(SubCategory)
    budget = models.FloatField(null=True)
    description = models.TextField()
    city = models.ManyToManyField(City)
    keywords = models.ManyToManyField(Keyword)
    views = models.IntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    files = models.ManyToManyField(FileProject)
    blacklisted_users = models.ManyToManyField(Profil,related_name="blacklisted_users_project")
    blacklisted_companies = models.ManyToManyField(Company,related_name="blacklisted_companies_project")

    downloaded_piecejointe_users = models.ManyToManyField(Profil,related_name="downloaded_piecejointe_users_project")
    downloaded_piecejointe_companies = models.ManyToManyField(Company,related_name="downloaded_piecejointe_companies_project")

    def __str__(self):
        return self.title

    def categories_s(self):
        cat = ''
        for c in self.categories.all():
            if c == self.categories.all().last():
                cat += c.name
            else:
                cat += c.name + ', '
        return cat

    def get_interested_mails(self):
        emails = []
        for company in self.downloaded_piecejointe_companies.all():
            emails.append(company.mail)
        for profil in self.downloaded_piecejointe_users.all():
            emails.append(profil.user.email)
        for contact in self.contact_set.all():
            emails.append(contact.company.mail)
        return remove_duplicates(emails)


    def cities_s(self):
        cities = ''
        for c in self.city.all():
            if c == self.city.all().last():
                cities += c.name
            else:
                cities += c.name + ', '
        return cities

    def other_project(self):
        return self.ao.project_set.all().exclude(id=self.id)

    def related_projects(self):
        cat = self.categories.all().values_list('id', flat=True)
        ids = self.ao.project_set.all().values_list('id', flat=True)
        return Project.objects.all().filter(categories__category__subcategory__in=cat).exclude(id__in=ids).distinct()[
               :4]

    def add_view(self):
        self.views += 1
        self.save()


    class Meta:
        verbose_name_plural = 'Lots'
        verbose_name = "Lot"

    def tracking_get_admin_url(self):
        return reverse('dashboard:ao_lot',kwargs={'id':self.id})

    def tracking_get_absolute_url(self):
        return reverse('ao:project', kwargs={'project_id':self.id,'id_ao':self.ao.id})

    def tracking_get_description(self):
        return self.title

#Offre poiur l'appel d'offre
class Offer(models.Model):
    user = models.ForeignKey(AOUser, on_delete=models.CASCADE)
    message = models.TextField()
    prod_date = models.IntegerField()
    price = models.FloatField()
    file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.__str__()

# Quand jesauvegarde une Appel d'offre
class AOSaves(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    ao = models.ForeignKey(AO, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ao.__str__()

# Quand je sauvegarde un lot
class PSaves(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project.__str__()

# Historique de contacte pour une AO
class AOContacted(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    ao = models.ForeignKey(AO, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ao.__str__()

#Historique de contacte pour un lot
class PContacted(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project.__str__()

#Le message de contact pour Appel offre ou Lot
class Contact(models.Model):
    ao = models.ForeignKey(AO, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    budget = models.CharField(max_length=10)
    days = models.IntegerField()
    message = models.TextField()
    file = models.FileField(null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.ao.__str__()


class ContactMail(models.Model):
    full_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    subject = models.CharField(max_length=100, null=True)
    message = models.TextField()
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.subject


class Newsletter(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()

    def __str__(self):
        return self.email

#Devis
class Quotation(models.Model):
    days = models.IntegerField()
    budget = models.CharField(max_length=50)
    message = models.TextField()
    tva = models.IntegerField()
    date_creation = models.DateTimeField(auto_now_add=True)
    ao = models.ForeignKey(AO, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.ao.title

    def amount(self):
        amount = 0
        for l in self.quotationline_set.all():
            amount += l.price * l.qte
        return amount

    def get_contact_mail(self):
        return self.company.mail

#Devis Line
class QuotationLine(models.Model):
    # price_number = models.FloatField()
    designation = models.CharField(max_length=50)
    unit = models.TextField(max_length=50)
    price = models.FloatField()
    qte = models.IntegerField()
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE)


class TVA(models.Model):
    tva = models.IntegerField(default=20)



#Singleton Accessible only by static method
class QuotationNbRows(models.Model):
    nb_rows = models.IntegerField(default=10)

    @staticmethod
    def get_value():
        try:
            q = QuotationNbRows.objects.all().first()
            return q.nb_rows
        except:
            QuotationNbRows.objects.create(nb_rows=10)
            return 10

    @staticmethod
    def update_value(value):
        try:
            q = QuotationNbRows.objects.all().first()
            q.nb_rows = value
            q.save()
        except:
            QuotationNbRows.objects.create(nb_rows=value)


def remove_duplicates(values):
    output = []
    seen = set()
    for value in values:
        # If value has not been encountered yet,
        # ... add it to both list and set.
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output

