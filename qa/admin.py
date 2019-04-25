from django.contrib import admin
from .models import *


admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(ContactMessage)
admin.site.register(Notification)
admin.site.register(SignalQuestion)
admin.site.register(SignalAnswer)
admin.site.register(SignalArticle)
admin.site.register(SignalComment)
