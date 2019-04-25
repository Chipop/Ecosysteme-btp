from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.conf.urls.static import settings, static
from . import views

app_name = "pusher_chat_app"

urlpatterns = [

    path('messenger/', views.messenger, name="messenger"),
    path('chatbox/', views.chatbox, name="chatbox"),
    # userid = user.id not  profile.id
    path('ajax/jwtkey/<int:userid>/', views.ajax_jwtkey, name="ajax_jwtkey"),
    path('ajax/userinfos/<int:userid>/', views.ajax_get_user_infos, name="ajax_get_user_infos"),

]
