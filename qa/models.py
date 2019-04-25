from django.db import models
from django.urls import reverse
from django.utils.deconstruct import deconstructible

from main_app.models import Profil

import time
import os
import uuid


# QA Model
class Category(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField()

    def __str__(self):
        return self.title


    class Meta:
        verbose_name_plural = 'QA Catégories'
        verbose_name = "QA Catégorie"

    def tracking_get_admin_url(self):
        return ""

    def tracking_get_absolute_url(self):
        return reverse('qa:category', kwargs={'category_id':self.id})

    def tracking_get_description(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=30)
    creation_date = models.DateTimeField(auto_now_add=True)
    create_by = models.ForeignKey(Profil, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'QA Tags'
        verbose_name = "QA Tag"

    def tracking_get_admin_url(self):
        return ""

    def tracking_get_absolute_url(self):
        return reverse('qa:blog_tag', kwargs={'tag_id':self.id})

    def tracking_get_description(self):
        return self.title


class Question(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    views_number = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag)
    shares = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return "/qa/question/%i/" % self.id

    def add_view(self):
        self.views_number = self.views_number + 1
        self.save()

    def add_share(self):
        self.shares = self.shares + 1
        self.save()

    @staticmethod
    def type_o():
        return 'question'

    class Meta:
        verbose_name_plural = 'Questions'
        verbose_name = "Question"

    def tracking_get_admin_url(self):
        return reverse('dashboard:qa_question', kwargs={'id_question':self.id})

    def tracking_get_absolute_url(self):
        return reverse('qa:question', kwargs={'qst_id':self.id})

    def tracking_get_description(self):
        return self.title


class Answer(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    likes = models.IntegerField(default=0)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return self.question.title

    def like(self):
        self.likes = self.likes + 1
        self.save()

    def dislike(self):
        self.likes = self.likes - 1
        self.save()

    @staticmethod
    def type_o():
        return 'answer'


# BLOG Model
# For rename the file before save
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


class Article(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(null=True)
    content = models.TextField()
    author = models.ForeignKey(Profil, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return "/qa/blog/article/%i/" % self.id

    def add_view(self):
        self.views += 1
        self.save()

    def like(self):
        self.likes = self.likes + 1
        self.save()

    def dislike(self):
        self.likes = self.likes - 1
        self.save()

    def add_share(self):
        self.shares = self.shares + 1
        self.save()

    @staticmethod
    def type_o():
        return 'article'

    class Meta:
        verbose_name_plural = 'QA Articles'
        verbose_name = "QA Article"

    def tracking_get_admin_url(self):
        return reverse('dashboard:qa_article', kwargs={'id_article':self.id})

    def tracking_get_absolute_url(self):
        return reverse('qa:blog_post', kwargs={'article_id':self.id})

    def tracking_get_description(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE, null=True)
    full_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    content = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.article.title

    def like(self):
        self.likes = self.likes + 1
        self.save()

    def dislike(self):
        self.likes = self.likes - 1
        self.save()


class ContactMessage(models.Model):
    name = models.CharField(max_length=60)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    send_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


class Notification(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    object = models.CharField(max_length=20)
    id_object = models.IntegerField()
    open = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)


class SignalQuestion(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profil, null=True, on_delete=models.SET_NULL)


class SignalAnswer(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profil, null=True, on_delete=models.SET_NULL)


class SignalArticle(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profil, null=True, on_delete=models.SET_NULL)


class SignalComment(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profil, null=True, on_delete=models.SET_NULL)
