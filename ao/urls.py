from django.urls import path

from ao import views

app_name = 'ao'

urlpatterns = [
    # HOME
    path('', views.index, name='home'),
    # SEARCH
    path('search/', views.search, name='search'),
    # AO
    path('<int:id_ao>/details/', views.ao_details, name='ao'),
    path('add/', views.add_ao, name='add_ao'),
    path('profile/ao/<int:ao_id>/delete/', views.delete_ao, name='delete_ao'),
    path('<int:ao_id>/edit/', views.edit_ao, name='edit_ao'),
    path('<int:ao_id>/edit/date/', views.update_date, name='edit_ao_date'),
    path('<int:ao_id>/devis/send/', views.send_quotation, name='send_quotation'),
    path('<int:ao_id>/devis/<int:devis_id>/details/', views.devis_details, name='devis'),
    # PROJECT
    path('<int:id_ao>/lot/<int:project_id>/', views.project_details, name='project'),
    path('<int:id_ao>/lot/<int:id_project>/edit/', views.edit_project, name='edit_project'),
    path('<int:id_ao>/lot/add/', views.add_project, name='add_project'),
    path('profile/lot/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    # CATEGORIES
    path('category/<int:category_id>/', views.category, name='category'),
    path('category/<cat_name>/<int:sub_category_id>/', views.sub_category, name='sub_category'),
    # CITY
    path('city/<int:city_id>/', views.city, name='city'),
    # PROFILE
    path('company/<int:company_id>/', views.company, name='company'),
    path('profile/<int:profile_id>/', views.profile, name='profile'),
    path('profile/update/', views.profile_settings, name='profile_settings'),
    path('profile/upgrade/', views.be_company, name='be_company'),
    # SAVES
    path('profile/<int:profile_id>/saves/', views.saves, name='saves'),
    path('profile/<int:profile_id>/saves/delete/<int:save_id>/', views.delete_save, name='save_delete'),
    path('profile/<int:profile_id>/saves/add/<int:id>/', views.add_save, name='add_save'),
    # CONTACTED
    path('profile/<int:profile_id>/contacted/delete/<int:contacted_id>/', views.delete_contacted,
         name='contact_delete'),
    path('profile/<int:profile_id>/contacted/', views.contacted, name='contacted'),
    # CONTACT US
    path('contact/', views.contact, name='contact'),
    # NEWSLETTER
    path('newsletter/subscribe/', views.add_newsletter, name='newsletter'),

    #AO Add users who downloaded document
    path('ao/<int:id>/download_document/', views.ao_download_document, name='ao_download_document'),

    # Project Add users who downloaded document
    path('project/<int:id>/download_document/', views.project_download_document, name='project_download_document'),
]
