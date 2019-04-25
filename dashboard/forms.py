from ckeditor.widgets import CKEditorWidget
from django import forms
from .models import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from ckeditor_uploader.fields import RichTextUploadingField
from SocialMedia.models import *
from main_app.models import Image as main_Image, Entreprise, Contact, Profil
from journal.models import *
from ecommerce.models import *
from qa.models import Question, Answer as QA_Answer, Category as QA_Category, Article as QA_Article

from eLearning.models import Category as  Elearning_Category, Question as Elearning_Question, \
    Answer as  Elearning_Answer, Cart   as Elearning_Cart, Chapter  as Elearning_Chapter, Coupon  as Elearning_Coupon, \
    Course  as Elearning_Course, Exam  as Elearning_Exam, Order as Elearning_Order, \
    OrderLine as Elearning_OrderLine, Formation as Elearning_Formation, Prerequisites  as Elearning_Prerequisites, \
    PostSkills  as Elearning_PostSkills, Sale as Elearning_Sale, SubCategory  as Elearning_SubCategory, \
    Part as Elearning_Part


#### GESTIONS ADMINS ####
class FormAdminAjout(forms.ModelForm):
    nom = forms.CharField(required=True)
    prenom = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    role = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    image = forms.ImageField(required=False)

    class Meta:
        model = Admin
        fields = ('nom', 'prenom', 'email', 'role', 'password', 'image')

    def clean(self):
        cleaned_data = super(FormAdminAjout, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        email = cleaned_data.get('email')

        if email and Admin.objects.filter(email=email).exists():
            self.add_error('email', "Cet E-mail est déjà enregistré.")

        if password != confirm_password:
            self.add_error("password", "Les deux mot de passes ne sont pas identiques.")

        try:
            validate_password(password=password, )
        except forms.ValidationError as e:
            error_message = list(e.messages)
            for error in error_message:
                self.add_error("password", error)


class FormAdminModification(forms.ModelForm):
    nom = forms.CharField(required=True)
    prenom = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    role = forms.CharField(required=True)
    image = forms.ImageField(required=False)

    class Meta:
        model = Admin
        fields = ('nom', 'prenom', 'email', 'role', 'image')

    def clean(self):
        cleaned_data = super(FormAdminModification, self).clean()

        email = cleaned_data.get('email')

        if email and Admin.objects.filter(email=email).exclude(id=self.instance.id).exists():
            self.add_error('email', "Cet E-mail est déjà enregistré.")


class FormAdminModifierPassword(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Admin
        fields = ('password',)

    def clean(self):
        cleaned_data = super(FormAdminModifierPassword, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error("password", "Les deux mot de passes ne sont pas identiques.")

        try:
            validate_password(password=password, )
        except forms.ValidationError as e:
            error_message = list(e.messages)
            for error in error_message:
                self.add_error("password", error)


class FormAdminModifierUserPassword(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('password',)

    def clean(self):
        cleaned_data = super(FormAdminModifierUserPassword, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error("password", "Les deux mot de passes ne sont pas identiques.")

        try:
            validate_password(password=password, )
        except forms.ValidationError as e:
            error_message = list(e.messages)
            for error in error_message:
                self.add_error("password", error)


#### NEWSLETTER ####
class FormAjoutCompagne(forms.ModelForm):
    class Meta:
        model = Compagne
        fields = ['contenu_email', 'titre']


#### RESEAU SOCIAL ####
class FormModifierGroupe(forms.ModelForm):
    class Meta:
        model = Groupe
        fields = ['nom', 'statut_groupe', 'description', 'admins', 'moderators']


class FormModifierProfil(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ['website', 'youtube', 'instagram', 'linkedin', 'twitter', 'ville', 'facebook',
                  "pays", 'resume',
                  'is_professional', 'is_journaliste', 'is_particulier', 'is_etudiant'
                  ]


class FormModifierUserSocial(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email'
                  ]


class FormModifierPageEntreprise(forms.ModelForm):
    presentation_entreprise = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = PageEntreprise
        fields = ['annee_creation', 'img_couverture', 'presentation_entreprise', 'siege_social', 'specialisation']


class FormModifierEntreprise(forms.ModelForm):
    class Meta:
        model = Entreprise
        fields = ['nom', 'logo']


class FormModifierOffreEmploi(forms.ModelForm):
    class Meta:
        model = OffreEmploi
        fields = ['tel', 'email', 'pays', 'ville', 'diplome_requis', 'type_contrat', 'description_poste',
                  'profil_recherche', 'type_emploi', 'nom_poste', 'fichier_joint', 'en_cours']


#### Journal ####
class FormModifierArticle(forms.ModelForm):
    class Meta:
        model = News
        fields = ['category', 'comment_enable', 'share_enable', 'title', 'small_title', 'tag', 'resume', 'content']


class FormModifierArticleVideo(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['video_url', 'category', 'comment_enable', 'share_enable', 'title', 'small_title', 'tag', 'resume',
                  'content']


class FormModifierJournaliste(forms.ModelForm):
    class Meta:
        model = Journalist
        fields = ['description', 'last_name', 'first_name', 'tel', 'facebook', 'twitter', 'instagram', 'youtube',
                  'google', 'linkedin', 'link']


#### ECOMMERCE ####
class FormModifierProduit(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'cat', 'brand', 'is_pro', 'packaging_detail', 'delivery_time', 'content',
            'price', 'quantity_min', 'unit', 'old_price', 'tags', 'price_from', 'image'
        ]


class FormEcommerceCategory(forms.ModelForm):
    class Meta:
        model = CommerceCategory
        fields = ['name', 'image']


class FormModifierBoutique(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['categories', 'name', 'address', 'tel', 'image_cover', 'image_profile', 'description']


##### Page de garde #####

class FormModifierProfilGarde(forms.ModelForm):
    date_naissance = forms.DateField(widget=forms.SelectDateWidget(attrs={'class': 'date-inline-block form-control'}))

    class Meta:
        model = Profil
        fields = ['website', 'youtube', 'instagram', 'linkedin', 'twitter', 'ville', 'facebook',
                  "pays", 'resume',
                  'is_professional', 'is_journaliste', 'is_particulier', 'is_etudiant',
                  'tel', 'telecopie', 'code_postal', 'adresse_profile', 'adresse_profile2',
                  'date_naissance',
                  'fonction', 'activite', 'service', 'taille_entreprise', 'departement',
                  ]


class FormModifierUserGarde(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email'
                  ]


class FormRepondreMessageContact(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['reponse']


class FormModifierQuestion(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditorWidget()
    )

    class Meta:
        model = Question
        fields = ['category', 'tags', 'title', 'content']


class FormModifierReponse(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditorWidget()
    )

    class Meta:
        model = QA_Answer
        fields = ['content']


class FormModifierQACategorie(forms.ModelForm):
    class Meta:
        model = QA_Category
        fields = ['description', 'title']


class FormModifierQAArticle(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditorWidget()
    )

    class Meta:
        model = QA_Article
        fields = ['content', 'title', 'tags', 'category', 'image']


class FormModifierMainImage(forms.ModelForm):
    image = forms.ImageField()

    class Meta:
        model = main_Image
        fields = '__all__'


class JournalistImageImport(forms.ModelForm):
    class Meta:
        model = ImageNews
        fields = ('image',)


class JournalistImagePrimaryImport(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image',)


class ProductImageImport(forms.ModelForm):
    class Meta:
        model = CommerceImage
        fields = ('image',)


############################## AO #############################


from ao.models import Company, AOUser, AO, Project, AOSaves, PSaves


class FormModifierProfilEntreprise(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['logo', 'name', 'activity', 'city', 'codePostal', 'address', 'description', 'mail', 'telephone',
                  'fax', 'trade_registry', 'facebook', 'twitter', 'youtube', 'linkedIn', 'github']


class FormModifierAO(forms.ModelForm):
    class Meta:
        model = AO
        fields = ['title', 'category',
                  'date_limit', 'contact_mail', 'contact_phone', 'time_limit', 'description', 'cloturee']


class FormModifierLot(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'categories',
                  'city', 'budget', 'keywords', 'description']


# ### Elearning Forms #####


class FormElearningCategory(forms.ModelForm):
    class Meta:
        model = Elearning_Category
        fields = ['name', 'image']


class FormElearningSubCategory(forms.ModelForm):
    class Meta:
        model = Elearning_SubCategory
        fields = ['name', 'category']


class FormElearningCours(forms.ModelForm):
    class Meta:
        model = Elearning_Course
        fields = ['name', 'description', 'category', 'welcome_msg', 'congratulation_msg', 'image', 'duration',
                  'has_certificate', 'is_free', 'price', 'language', 'level', 'video_url', 'related_courses']


class FormElearningPrerequis(forms.ModelForm):
    class Meta:
        model = Elearning_Prerequisites
        fields = ['value']


class FormElearningPostSkill(forms.ModelForm):
    class Meta:
        model = Elearning_PostSkills
        fields = ['value']


class FormElearningChapitre(forms.ModelForm):
    class Meta:
        model = Elearning_Part
        fields = ['name', 'attached_file', 'is_free', "number"]


class FormElearningLecon(forms.ModelForm):
    class Meta:
        model = Elearning_Chapter
        fields = ['name', 'content', 'video_url', "duration", 'number', 'video_file']


class FormElearningCoupon(forms.ModelForm):
    class Meta:
        model = Elearning_Coupon
        fields = ['value', 'percentage', 'used', "is_multiple", 'is_general', 'course']


class FormElearningSales(forms.ModelForm):
    date_end = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = Elearning_Sale
        fields = ['course', 'percentage', 'date_end', "is_daily", ]
