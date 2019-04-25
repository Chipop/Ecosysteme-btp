from ckeditor.fields import RichTextField
from django.db import models
import os
import uuid
import time
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from main_app.models import Profil


@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        # eg: filename = 'my uploaded file.jpg'
        ext = filename.split('.')[-1]  # eg: 'jpg'
        uid = uuid.uuid4().hex[:10]  # eg: '567ae32f97'

        # eg: 'my-uploaded-file'
        new_name = '-'.join(filename.replace('.%s' % ext, '').split())

        # eg: 'my-uploaded-file_64c942aa64.jpg'
        renamed_filename = '%(new_name)s_%(uid)s.%(ext)s' % {'new_name': new_name, 'uid': uid, 'ext': ext}

        # eg: 'images/2017/01/29/my-uploaded-file_64c942aa64.jpg'
        return os.path.join(self.path, renamed_filename)


class Category(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    image_path = time.strftime('images/%Y/%m/%d')
    image = models.ImageField(upload_to=PathAndRename(image_path))

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="elearning_subcategory_set")

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=300, null=False, blank=False)
    description = RichTextField(null=False, blank=False)
    is_free = models.BooleanField(default=True, null=False, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0, blank=True)
    duration = models.CharField(max_length=20, null=False, blank=False)
    date_add = models.DateField(auto_now_add=True, blank=True)
    image_path = time.strftime('images/%Y/%m/%d')
    image = models.ImageField(upload_to=PathAndRename(image_path))
    video_url = models.URLField(null=True, blank=True)
    like = models.IntegerField(default=0, null=False, blank=True)
    view = models.IntegerField(default=0, null=False, blank=True)
    share = models.IntegerField(default=0, null=False, blank=True)
    language = models.CharField(max_length=300, null=False, blank=False)
    level = models.CharField(max_length=300, null=False, blank=False)
    has_certificate = models.BooleanField(default=False, null=False, blank=True)
    active = models.BooleanField(default=True, null=False, blank=True)
    approved = models.BooleanField(default=False, null=False, blank=True)
    to_evaluate = models.BooleanField(default=False, null=False, blank=True)
    refused = models.BooleanField(default=False, null=False, blank=True)
    welcome_msg = RichTextField(null=True, blank=True)
    congratulation_msg = RichTextField(null=True, blank=True)
    teacher = models.ForeignKey(Profil, on_delete=models.SET_NULL, null=True, blank=False, related_name="elearning_course_set")
    category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=False, related_name="elearning_course_set")
    related_courses = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.name

    def add_like(self):
        self.like += 1
        self.save()

    def add_view(self):
        self.view += 1
        self.save()

    def add_share(self):
        self.share += 1
        self.save()

    def delete_course(self):
        self.active = False
        self.save()

    def evaluate(self):
        self.to_evaluate = True
        self.save()


class Prerequisites(models.Model):
    value = models.CharField(max_length=300, null=False, blank=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False, blank=False, related_name="elearning_prerequisites_set")

    def __str__(self):
        return "{} - {}".format(self.value, self.course.name)


class PostSkills(models.Model):
    value = models.CharField(max_length=300, null=False, blank=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False, blank=False, related_name="elearning_postskills_set")

    def __str__(self):
        return "{} - {}".format(self.value, self.course.name)


class Coupon(models.Model):
    value = models.CharField(max_length=300, null=False, blank=False)
    percentage = models.IntegerField(null=False, blank=False)
    used = models.BooleanField(default=False)
    is_multiple = models.BooleanField(default=False, null=False)
    is_general = models.BooleanField(default=False, null=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name="elearning_coupon_set")

    def __str__(self):
        return self.value


class Part(models.Model):
    name = models.CharField(max_length=300, null=False, blank=False)
    number = models.IntegerField(null=False, blank=False)
    attached_file = models.FileField(null=True, blank=True, upload_to=PathAndRename(time.strftime('attached_files/%Y/%m/%d')))
    attached_file_url = models.URLField(null=True, blank=True)
    date_add = models.DateField(auto_now_add=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False, blank=False, related_name="elearning_part_set")
    is_free = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {}".format(self.name, self.course.name)


class Chapter(models.Model):
    name = models.CharField(max_length=300, null=False, blank=False)
    number = models.IntegerField(null=False, blank=False)
    content = models.TextField(null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    duration = models.CharField(max_length=20, null=False, blank=False)
    video_path = time.strftime('videos/%Y/%m/%d')
    video_file = models.FileField(upload_to=PathAndRename(video_path), null=True, blank=True)
    date_add = models.DateField(auto_now_add=True, blank=True)
    part = models.ForeignKey(Part, on_delete=models.CASCADE, null=False, blank=False, related_name="elearning_chapter_set")

    def __str__(self):
        return self.name


class Ratting(models.Model):
    value = models.IntegerField(null=False, blank=False)
    comment = models.TextField(blank=True)
    date_add = models.DateField(auto_now_add=True, editable=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False, blank=False, related_name="elearning_ratting_set")
    student = models.ForeignKey(Profil, on_delete=models.CASCADE, null=False, blank=False, related_name="elearning_ratting_set")

    def __str__(self):
        return "vote {0},  {1} : {2}".format(str(self.pk), str(self.value), self.course.name)


class Sale(models.Model):
    percentage = models.IntegerField(null=False, blank=False)
    date_end = models.DateTimeField(blank=False, default=timezone.now)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False, blank=False, related_name="elearning_sale_set")
    is_daily = models.BooleanField(default=False)

    def __str__(self):
        return str(self.percentage) + "% for " + self.course.name

    def new_price(self):
        return self.course.price - ((self.course.price * self.percentage) / 100) 


class WishList(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name="eLearning_wishlist_set")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="eLearning_wishlist_set")

    def __str__(self):
        return self.user.user.username + ' wish ' + self.course.name


class Cart(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name="elearning_cart_set")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="elearning_cart_set")
    date_add = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return '{0} de {1}'.format(self.course.name, self.user.user.username)


class Formation(models.Model):
    date_start = models.DateField(auto_now_add=True, editable=True)
    student = models.ForeignKey(Profil, on_delete=models.CASCADE, null=True, blank=False, related_name="elearning_formation_set")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=False, related_name="elearning_formation_set")

    def __str__(self):
        return self.student.user.username + ', studies ' + self.course.name


class Progress(models.Model):
    student = models.ForeignKey(Profil, on_delete=models.CASCADE, null=True, blank=False, related_name="elearning_progress_set")
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, null=True, blank=False, related_name="elearning_progress_set")
    date_add = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)

    def __str__(self):
        return self.student.user.username + ' progress in ' + self.chapter.name


class Order(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    date_add = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=200, default="Created")
    date_payment = models.DateField(null=True, blank=True)
    date_complete = models.DateField(null=True, blank=True)
    student = models.ForeignKey(Profil, on_delete=models.SET_NULL, null=True, related_name="elearning_order_set")

    def __str__(self):
        return 'Order {0} de {1}'.format(str(self.pk), self.student.user.username)


class OrderLine(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="elearning_orderline_set")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name="elearning_orderline_set")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, related_name="elearning_orderline_set")

    def __str__(self):
        return "oder {} {}".format(self.order.id, self.course.name)


class Exam(models.Model):
    title = models.CharField(max_length=300, null=True, blank=True)
    description = RichTextField(null=True, blank=True)
    part = models.OneToOneField(Part, on_delete=models.CASCADE, null=True, blank=False)

    def __str__(self):
        return self.title


class Question(models.Model):
    text = RichTextField(null=False, blank=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True, blank=False, related_name="elearning_question_set")
    explanation = RichTextField(null=True, blank=True)
    is_multiple = models.BooleanField(null=False, default=False)

    def __str__(self):
        return "{}".format(self.exam.title)


class Choice(models.Model):
    value = models.TextField(null=False, blank=False)
    is_correct = models.BooleanField(null=False, default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=False, related_name='elearning_choice_set')

    def __str__(self):
        return "{} - {}".format(self.question, self.value[:40])


class Answer(models.Model):
    score = models.IntegerField(null=True, blank=True)
    date_add = models.DateField(auto_now_add=True)
    student = models.ForeignKey(Profil, on_delete=models.CASCADE, null=False,related_name="elearning_answer_set")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True, blank=False, related_name="elearning_answer_set")


class ResultSearch(models.Model):
    key_word = models.CharField(max_length=255, null=True, blank=True)
    date_add = models.DateField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="elearning_resultsearch_set")


class MessageToTeacher(models.Model):
    object = models.CharField(max_length=300, null=False, blank=False)
    message = RichTextField(blank=False, null=False)
    date_add = models.DateTimeField(auto_now_add=True, editable=True)
    is_read = models.BooleanField(default=False)
    teacher = models.ForeignKey(Profil, on_delete=models.CASCADE, null=False, blank=False, related_name='teacher')
    student = models.ForeignKey(Profil, on_delete=models.CASCADE, null=False, blank=False, related_name='student')

    def __str__(self):
        return "{0} {1}".format(str(self.pk), self.student)


class MessageToStudent(models.Model):
    message = RichTextField(blank=False, null=False)
    date_add = models.DateTimeField(auto_now_add=True, editable=True)
    is_read = models.BooleanField(default=False)
    parent_message = models.ForeignKey(MessageToTeacher, on_delete=models.CASCADE, null=False, blank=False, related_name="elearning_messagetostudent_set")

    def __str__(self):
        return "{0} {1}".format(str(self.pk), self.parent_message.student)


class MailingCourse(models.Model):
    object = models.CharField(max_length=300, null=False, blank=False)
    message = RichTextField(blank=False, null=False)
    date_add = models.DateTimeField(auto_now_add=True, editable=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=False, blank=False, related_name="elearning_mailingcourse_set")

    def __str__(self):
        return "{0} {1}".format(str(self.course.teacher), self.course.name)


class Counter():
    count_x = 0
    count_y = 0

    def increment_x(self):
        self.count_x += 1
        return ''

    def increment_y(self):
        self.count_y += 1
        return ''
