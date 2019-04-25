from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include, url
from django.conf.urls.static import settings, static
from main_app.views import *
from ckeditor_uploader import views as ckeditor_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include("dashboard.urls")),
    path('ao/', include("ao.urls")),
    path('reseausocial/', include("SocialMedia.urls")),
    path('journal/', include("journal.urls")),
    path('e_commerce/', include(('ecommerce.urls'), namespace='e_commerce')),
    path('qa/', include(('qa.urls'), namespace='qa')),
    path('e_learning/', include(('eLearning.urls'), namespace='eLearning')),
    path('', include("main_app.urls")),

    re_path(r'^paypal/', include('paypal.standard.ipn.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^ckeditor/upload/', ckeditor_views.upload, name='ckeditor_upload'),
    url(r'^ckeditor/browse/', ckeditor_views.browse, name='ckeditor_browse'),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^select2/', include('django_select2.urls')),
    path('chat/', include("pusher_chat_app.urls"), name="pusher_chat_app"),
]

handler400 = error_400
handler403 = error_403
handler404 = error_404
handler500 = error_500

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
