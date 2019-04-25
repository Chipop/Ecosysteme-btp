from django.contrib import admin
from .models import *


class ProgressAdmin(admin.ModelAdmin):
    list_filter = ('student', )


admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Course)
admin.site.register(Prerequisites)
admin.site.register(PostSkills)
admin.site.register(Part)
admin.site.register(Chapter)
admin.site.register(Ratting)
admin.site.register(Sale)
admin.site.register(Cart)
admin.site.register(WishList)
admin.site.register(Formation)
admin.site.register(Progress, ProgressAdmin)
admin.site.register(Order)
admin.site.register(OrderLine)
admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Answer)
admin.site.register(MessageToTeacher)
admin.site.register(MessageToStudent)
admin.site.register(MailingCourse)
admin.site.register(Coupon)
