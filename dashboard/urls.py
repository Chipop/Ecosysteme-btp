from django.urls import path
from dashboard import views

app_name = 'dashboard'
urlpatterns = [


    ######################### PARAMETRES ~~################################################

    path('parametres/', views.parametres, name='parametres'),

    ######################### TRACKING ~~################################################

    path('tracking/visites/', views.tracking_visites, name='tracking_visites'),
    path('tracking/visite/<int:id_visite>/', views.tracking_visite, name='tracking_visite'),

    ################################     Espace Administrateurs    ################################
    # Liste des admins
    path('admin/admins_list/', views.admin_admins_list, name='admin_admins_list'),
    path('admin/delete_admins/', views.delete_admins, name='delete_admins'),
    path('admin/delete_admin/<int:id_admin>/', views.delete_admin, name='delete_admin'),
    path('admin/update_admin/<int:id_admin>/', views.update_admin, name='update_admin'),
    path('admin/update_admin/informations/<int:id_admin>/', views.update_admin_informations, name='update_admin_informations'),
    path('admin/update_admin/password/<int:id_admin>/', views.update_admin_password,
         name='update_admin_password'),

    #Add Admin
    path('admin/add_admin/', views.admin_add_admin, name='admin_add_admin'),
    #Admin Profile
    path('admin/admin_profile/<int:id_admin>/', views.admin_profile, name='admin_profile'),


    ################################    Page de garde    ################################
    #Vue Generale
    path('main/general_view/', views.page_garde_general_view, name='page_garde_general_view'),

    # Messages
    path('main/messages/', views.main_messages, name='main_messages'),
    path('main/message/<int:id_message>/', views.vue_message, name='vue_message'),
    path('main/delete_messages/', views.delete_messages, name='delete_messages'),
    path('main/repondre_message/<int:id_message>/', views.repondre_message, name='repondre_message'),

    #Utilisateurs
    path('main/users_list/', views.users_list, name='users_list'),
    path('main/blacklisted_users_list/', views.blacklisted_users_list, name='blacklisted_users_list'),
    path('main/user_infos/<int:id_user>/', views.user_infos, name='user_infos'),
    path('main/delete_user/<int:id_user>/', views.delete_user, name='delete_user'),
    path('main/update_user/<int:id_user>/', views.update_user,
         name='update_user'),
    path('main/update_user_infos/<int:id_user>/', views.update_user_infos,
         name='update_user_infos'),

    path('main/update_user_password/<int:id_profil>/', views.update_user_password,
         name='update_user_password'),

    path('main/update_profile_pic/<int:id_user>/', views.main_update_profile_pic,
         name='main_update_profile_pic'),
    path('main/update_cover_pic/<int:id_user>/', views.main_update_cover_pic,
         name='main_update_cover_pic'),
        #Ajax Utilisateurs
    path('main/delete_users/', views.delete_users, name='delete_users'),

    path('main/verify_users/', views.verify_users, name='verify_users'),
    path('main/deverify_users/', views.deverify_users, name='deverify_users'),

    path('main/activate_users/', views.activate_users, name='activate_users'),
    path('main/desactivate_users/', views.desactivate_users, name='desactivate_users'),

    path('main/blacklist_users/', views.blacklist_users, name='blacklist_users'),
    path('main/deblacklist_users/', views.deblacklist_users, name='deblacklist_users'),










    ################################     Newsletter    ################################
    path('main/newsletter/', views.newsletter, name='newsletter'),
    path('main/newsletter/emails_list/', views.emails_list, name='emails_list'),
    path('main/newsletter/add_email/', views.add_email, name='add_email'),
    path('main/newsletter/delete_emails/', views.delete_emails, name='delete_emails'),
    path('main/newsletter/compagnes/', views.compagnes, name='compagnes'),
    path('main/newsletter/delete_compagnes/', views.delete_compagnes, name='delete_compagnes'),
    path('main/newsletter/lancer_compagne/', views.lancer_compagne_new, name='lancer_compagne_new'),
    path('main/newsletter/lancer_compagne_add_emails/', views.lancer_compagne_add_emails, name='lancer_compagne_add_emails'),
    path('main/newsletter/old_compagne_add_emails/<int:id_compagne>/', views.old_compagne_add_emails, name='old_compagne_add_emails'),
    #
    path('main/newsletter/lancer_compagne_emails/<int:id_compagne>/', views.lancer_compagne_emails, name='lancer_compagne_emails'),
    path('main/newsletter/lancer_compagne_contenu/<int:id_compagne>/', views.lancer_compagne_contenu, name='lancer_compagne_contenu'),
    path('main/newsletter/lancer_compagne_confirmation/<int:id_compagne>/', views.lancer_compagne_confirmation,
         name='lancer_compagne_confirmation'),
    path('main/newsletter/lancer_compagne_validation/<int:id_compagne>/', views.lancer_compagne_validation,
         name='lancer_compagne_validation'),

    path('main/newsletter/image_load/<int:id_compagne>/', views.email_seen, name='email_seen'),
    path('main/newsletter/delete_compagne/<int:id_compagne>/', views.delete_compagne, name='delete_compagne'),








    ################################      Social Media   ################################
    #Vue Generale
    path('socialmedia/general_view/', views.socialmedia_general_view, name='socialmedia_general_view'),

    #Groupes
    path('socialmedia/groups_list/', views.socialmedia_groups_list, name='socialmedia_groups_list'),
    path('socialmedia/infos_group/<int:id_group>/', views.infos_group, name='socialmedia_infos_group'),
    path('socialmedia/delete_groups/', views.socialmedia_delete_groups, name='socialmedia_delete_groups'),
    path('socialmedia/delete_group/<int:id_group>/', views.socialmedia_delete_group, name='socialmedia_delete_group'),
    path('socialmedia/update_group/<int:id_group>/', views.socialmedia_update_group, name='socialmedia_update_group'),
    path('socialmedia/socialmedia_update_group_infos/<int:id_group>/', views.socialmedia_update_group_infos, name='socialmedia_update_group_infos'),

    path('socialmedia/update_groupe_profile_pic/<int:id_group>/', views.socialmedia_update_groupe_profile_pic,
         name='socialmedia_update_groupe_profile_pic'),
    path('socialmedia/update_groupe_cover_pic/<int:id_group>/', views.socialmedia_update_groupe_cover_pic,
         name='socialmedia_update_groupe_cover_pic'),


    #Profils
    path('socialmedia/profils_list/', views.socialmedia_profils_list, name='socialmedia_profils_list'),
    path('socialmedia/infos_profile/<int:id_user>/', views.infos_profile, name='socialmedia_infos_profile'),
    path('socialmedia/delete_profils/', views.socialmedia_delete_profils, name='socialmedia_delete_profils'),
    path('socialmedia/delete_profil/<int:id_profil>/', views.socialmedia_delete_profile, name='socialmedia_delete_profile'),
    path('socialmedia/update_profil/<int:id_profil>/', views.socialmedia_update_profil,
         name='socialmedia_update_profil'),
    path('socialmedia/update_profil_infos/<int:id_profil>/', views.socialmedia_update_profil_infos,
         name='socialmedia_update_profil_infos'),

    path('socialmedia/update_profile_pic/<int:id_user>/', views.socialmedia_update_profile_pic,
         name='socialmedia_update_profile_pic'),
    path('socialmedia/update_cover_pic/<int:id_user>/', views.socialmedia_update_cover_pic,
         name='socialmedia_update_cover_pic'),

    #Page Entreprise
    path('socialmedia/page_entreprise_list/', views.socialmedia_page_entreprise_list, name='socialmedia_page_entreprise_list'),
    path('socialmedia/infos_page_entreprise/<int:id_page_entreprise>/', views.infos_page_entreprise, name='socialmedia_infos_page_entreprise'),
    path('socialmedia/delete_pages_entreprises/', views.socialmedia_delete_pages_entreprises, name='socialmedia_delete_pages_entreprises'),
    path('socialmedia/delete_page_entreprise/<int:id_page_entreprise>/', views.socialmedia_delete_page_entreprise,
         name='socialmedia_delete_page_entreprisee'),
    path('socialmedia/update_page_entreprise/<int:id_page_entreprise>/', views.socialmedia_update_page_entreprise,
         name='socialmedia_update_page_entreprise'),

    #Offres d'emploi
    path('socialmedia/offre_emploi_list/', views.socialmedia_offre_emploi_list, name='socialmedia_offre_emploi_list'),
    path('socialmedia/infos_offre_emploi/<int:id_offre_emploi>/', views.infos_offre_emploi, name='socialmedia_infos_offre_emploi'),
    path('socialmedia/delete_offre_emploi/', views.socialmedia_delete_offre_emploi,
         name='socialmedia_delete_offre_emploi'),
    path('socialmedia/delete_offre_emploi/<int:id_offre_emploi>/', views.socialmedia_delete_offre_emploi_one,
         name='socialmedia_delete_offre_emploi_one'),
    path('socialmedia/update_offre_emploi/<int:id_offre_emploi>/', views.socialmedia_update_offre_emploi,
         name='socialmedia_update_offre_emploi'),
        #ajax
    path('socialmedia/offre_encours/', views.socialmedia_offre_encours,
         name='socialmedia_offre_encours'),
    path('socialmedia/offre_finie/', views.socialmedia_offre_finie,
         name='socialmedia_offre_finie'),

    #Publications
    path('socialmedia/publications/', views.socialmedia_publications, name='socialmedia_publications'),
    path('socialmedia/infos_publication/<int:id_publication>/', views.infos_publication, name='socialmedia_infos_publication'),
    path('socialmedia/delete_publications/', views.socialmedia_delete_publications,
             name='socialmedia_delete_publications'),
    path('socialmedia/delete_publication/<int:id_publication>/', views.socialmedia_delete_publication,
         name='socialmedia_delete_publication'),
    path('socialmedia/update_publication/<int:id_publication>/', views.socialmedia_update_publication_all,
         name='socialmedia_update_publication_all'),
    path('socialmedia/update_publication/update/<int:id_publication>/', views.socialmedia_update_publication,
             name='socialmedia_update_publication'),
    path('socialmedia/update_publication_comment/<int:id_publication>/<int:id_comment>/', views.socialmedia_update_publication_comment,
             name='socialmedia_update_publication_comment'),
    path('socialmedia/update_publication_reply/<int:id_publication>/<int:id_reply>/', views.socialmedia_update_publication_reply,
         name='socialmedia_update_publication_reply'),

    path('socialmedia/signal/<int:id_signal>/', views.socialmedia_activate_signal,
         name='socialmedia_activate_signal'),









    ################################      News     ################################
    #Vue Generale
    path('news/general_view/', views.news_general_view, name='news_general_view'),


    #Articles
    path('news/articles/', views.news_articles, name='news_articles'),
    path('news/article/<int:id_article>/', views.news_infos_article, name='news_infos_article'),
    path('news/delete_articles/', views.delete_articles, name='delete_articles'),
    path('news/delete_article/<int:id_article>/', views.delete_article, name='delete_article'),
    path('news/update_article/<int:id_article>/', views.update_article, name='update_article'),
    path('news/update_primary_image/<int:article_id>/', views.news_update_primary_image,
         name='news_update_primary_image'),
    path('news/update_image/<int:article_id>/', views.news_update_image, name='news_update_image'),

    path('news/delete_image_update/<int:article_id>/<int:image_id>/', views.news_delete_image_update,
         name="news_delete_image_update"),

    #Ajax
    path('news/activer_articles/', views.activer_articles, name='activer_articles'),
    path('news/desactiver_articles/', views.desactiver_articles, name='desactiver_articles'),
    path('news/verifier_articles/', views.verifier_articles, name='verifier_articles'),
    path('news/deverifier_articles/', views.deverifier_articles, name='deverifier_articles'),

    path('news/signaler_articles/', views.signaler_articles, name='signaler_articles'),
    path('news/designaler_articles/', views.designaler_articles, name='designaler_articles'),


    # Articles videos
    path('news/articles_videos/', views.news_articles_videos, name='news_articles_videos'),
    path('news/article_videos/<int:id_article_videos>/', views.news_infos_article_videos, name='news_infos_article_videos'),
    path('news/delete_articles_videos/', views.delete_articles_videos, name='delete_articles_videos'),
    path('news/delete_article_video/<int:id_article_video>/', views.delete_article_video, name='delete_article_video'),
    path('news/update_article_video/<int:id_article>/', views.update_article_video, name='update_article_video'),
    # Ajax
    path('news/activer_articles_videos/', views.activer_articles_videos, name='activer_articles_videos'),
    path('news/desactiver_articles_videos/', views.desactiver_articles_videos, name='desactiver_articles_videos'),
    path('news/verifier_article_videoss/', views.verifier_articles_videos, name='verifier_articles_videos'),
    path('news/deverifier_articles_videos/', views.deverifier_articles_videos, name='deverifier_articles_videos'),


    #Journalistes
    path('news/journalistes/', views.news_journalistes, name='news_journalistes'),
    path('news/journaliste/<int:id_journaliste>/', views.news_infos_journaliste, name='news_infos_journaliste'),
    path('news/delete_journalistes/', views.delete_journalistes, name='delete_journalistes'),
    path('news/delete_journaliste/<int:id_journaliste>/', views.delete_journaliste, name='delete_journaliste'),
    path('news/update_journaliste/<int:id_journaliste>/', views.update_journaliste, name='update_journaliste'),


    # Signalements
    path('news/signalements/', views.news_signalements, name='news_signalements'),
    path('news/delete_signalements/', views.delete_signalements, name='delete_signalements'),

    #Réseaux sociaux + Bannieres
    path('news/reseaux_bannieres/', views.news_reseaux_bannieres, name='news_reseaux_bannieres'),

    #Commentaires #Article_type = normal,video
    path('news/delete_comment/<int:id_comment>/<str:article_type>/', views.news_delete_comment, name='news_delete_comment'),
    path('news/delete_answer/<int:id_answer>/<str:article_type>/', views.news_delete_answer, name='news_delete_answer'),



    ################################     Market Place     ################################
    #Vue Generale
    path('marketplace/general_view/', views.marketplace_general_view, name='marketplace_general_view'),

    #Commandes
    path('marketplace/orders/', views.marketplace_orders, name='marketplace_orders'),
    path('marketplace/order/<int:id_order>/', views.marketplace_order, name='marketplace_order'),
    path('marketplace/delete_orders/', views.delete_orders, name='delete_orders'),
    path('marketplace/change_commande_status/<str:status_name>/', views.change_commande_status, name='change_commande_status'),

    # Produits
    path('marketplace/products/', views.marketplace_products, name='marketplace_products'),
    path('marketplace/products_to_approve/', views.marketplace_products_to_approve, name='marketplace_products_to_approve'),
    path('marketplace/product/<int:id_product>/', views.marketplace_product, name='marketplace_product'),
    path('marketplace/delete_products/', views.delete_products, name='delete_products'),
    path('marketplace/approve_products/', views.approve_products, name='approve_products'),
    path('marketplace/desapprove_products/', views.desapprove_products, name='desapprove_products'),
    path('marketplace/vente_products/', views.vente_products, name='vente_products'),
    path('marketplace/non_vente_products/', views.non_vente_products, name='non_vente_products'),
    path('marketplace/delete_product/<int:id_product>/', views.delete_product, name='delete_product'),
    path('marketplace/update_product/<int:id_product>/', views.update_product, name='update_product'),

    path('products/update/upload_image/<int:product_id>/', views.up_product_upload_image,
         name='up_product_upload_image'),
    path('products/update/delete_image/<int:image_id>/', views.up_product_delete_image,
         name='up_product_delete_image'),

    #Boutiques
    path('marketplace/shops/', views.marketplace_shops, name='marketplace_shops'),
    path('marketplace/shop/<int:id_shop>/', views.marketplace_shop, name='marketplace_shop'),
    path('marketplace/delete_shops/', views.delete_shops, name='delete_shops'),
    path('marketplace/approve_shops/', views.approve_shops, name='approve_shops'),
    path('marketplace/delete_shop/<int:id_shop>/', views.delete_shop, name='delete_shop'),
    path('marketplace/update_shop/<int:id_shop>/', views.update_shop, name='update_shop'),

    # Bannieres et réseaux sociaux
    path('marketplace/reseaux_bannieres/', views.marketplace_reseaux_bannieres, name='marketplace_reseaux_bannieres'),


    # Demandes Exposants
    path('marketplace/exposants_requests/', views.marketplace_exposants_requests, name='marketplace_exposants_requests'),

    # Gestion Categories
    path('marketplace/add_category/', views.marketplace_add_category_level_one, name='marketplace_add_category_level_one'),

    path('marketplace/manage_categories/', views.marketplace_manage_categories, name='marketplace_manage_categories'),
    path('marketplace/add_category/level_<int:category_level>/parent_<int:category_parent_id>/', views.marketplace_add_category, name='marketplace_add_category'),
    path('marketplace/update_category/level_<int:category_level>/parent_<int:category_id>/', views.marketplace_update_category, name='marketplace_update_category'),
    path('marketplace/delete_category/level_<int:category_level>/parent_<int:category_id>/',  views.marketplace_delete_category, name='marketplace_delete_category'),


    ################################    Q and A    ################################
    #Vue Generale
    path('qa/general_view/', views.qa_general_view, name='qa_general_view'),
    #Questions
    path('qa/questions/', views.qa_questions, name='qa_questions'),
    path('qa/question/<int:id_question>/', views.qa_question, name='qa_question'),
    path('qa/delete_question/<int:id_question>/', views.delete_question, name='delete_question'),
    path('qa/update_question/<int:id_question>/', views.update_question, name='update_question'),
    path('qa/question_delete_signals/<int:id_question>/', views.question_delete_signals, name='question_delete_signals'),

    #Ajax
    path('qa/delete_questions/', views.delete_questions, name='delete_questions'),

    #Reponses
    path('qa/reponses/', views.qa_reponses, name='qa_reponses'),
    path('qa/reponse/<int:id_reponse>/', views.qa_reponse, name='qa_reponse'),
    path('qa/delete_reponse/<int:id_reponse>/', views.delete_reponse, name='delete_reponse'),
    path('qa/update_reponse/<int:id_reponse>/', views.update_reponse, name='update_reponse'),

    path('qa/reponse_delete_signals/<int:id_reponse>/', views.reponse_delete_signals,
         name='reponse_delete_signals'),
        #Ajax
    path('qa/delete_reponses/', views.delete_reponses, name='delete_reponses'),


    # Categories
    path('qa/categories/', views.qa_categories, name='qa_categories'),
    path('qa/categories/<int:id_category>/questions/', views.qa_category_question, name='qa_category_question'),
    path('qa/add_category/', views.qa_add_category, name='qa_add_category'),
    path('qa/delete_category/<int:id_category>/', views.qa_delete_category, name='qa_delete_category'),
    path('qa/update_category/<int:id_category>/', views.qa_update_category, name='qa_update_category'),

    # Ajax
    path('qa/delete_categories/', views.qa_delete_categories, name='qa_delete_categories'),


    #Articles BLOG QA
    path('qa/articles/', views.qa_articles, name='qa_articles'),
    path('qa/article/<int:id_article>/', views.qa_article, name='qa_article'),
    path('qa/delete_article/<int:id_article>/', views.qa_delete_article, name='qa_delete_article'),
    path('qa/update_article/<int:id_article>/', views.qa_update_article, name='qa_update_article'),

    path('qa/delete_comment/<int:id>/', views.qa_delete_comment,
         name='qa_delete_comment'),

        #Ajax
    path('qa/delete_articles/', views.qa_delete_articles, name='qa_delete_articles'),

    #Experts
    path('qa/experts/', views.qa_experts, name='qa_experts'),

    # Signalements :

    path('qa/signalements/', views.qa_signalements, name='qa_signalements'),
    path('qa/delete_signalements/', views.qa_delete_signalements, name='qa_delete_signalements'),

    path('qa/article_delete_signals/<int:id>/', views.qa_article_delete_signals,
         name='qa_article_delete_signals'),

    path('qa/comment_delete_signals/<int:id>/', views.qa_comment_delete_signals,
         name='qa_comment_delete_signals'),

    ################################    Appel Offres    ################################
    # Vue Generale
    path('ao/general_view/', views.ao_general_view, name='ao_general_view'),
    #Profil Entreprise
    path('ao/profils_entreprises/', views.ao_profils_entreprises, name='ao_profils_entreprises'),
    path('ao/profil_entreprise/<int:id>/', views.ao_profil_entreprise, name='ao_profil_entreprise'),
    path('ao/delete_profil_entreprise/<int:id>/', views.ao_delete_profil_entreprise, name='ao_delete_profil_entreprise'),
    path('ao/delete_profils_entrepriss/', views.ao_delete_profils_entreprises, name='ao_delete_profils_entreprises'),
    path('ao/update_profil_entreprise/<int:id>/', views.ao_update_profil_entreprise, name='ao_update_profil_entreprise'),

    # Particuliers
    path('ao/profils_particuliers/', views.ao_profils_particuliers, name='ao_profils_particuliers'),

    #Appels Offres

    path('ao/appels_offres/', views.ao_appels_offres, name='ao_appels_offres'),
    path('ao/delete_aos/', views.ao_delete_aos, name='ao_delete_aos'),
    path('ao/appel_offre/<int:id>/', views.ao_appel_offre, name='ao_appel_offre'),
    path('ao/delete_appel_offre/<int:id>/', views.ao_delete_appel_offre, name='ao_delete_appel_offre'),
    path('ao/update_appel_offre/<int:id>/', views.ao_update_appel_offre, name='ao_update_appel_offre'),

    ##Lots ##

    path('ao/lots/', views.ao_lots, name='ao_lots'),
    path('ao/delete_lots/', views.ao_delete_lots, name='ao_delete_lots'),
    path('ao/lot/<int:id>/', views.ao_lot, name='ao_lot'),
    path('ao/delete_lot/<int:id>/', views.ao_delete_lot, name='ao_delete_lot'),
    path('ao/update_lot/<int:id>/', views.ao_update_lot, name='ao_update_lot'),

    ## Devis ##

    path('ao/devis/', views.ao_devis, name='ao_devis'),
    path('ao/delete_devis_list/', views.ao_delete_devis_list, name='ao_delete_devis_list'),
    path('ao/devis/<int:id>/', views.ao_devis_one, name='ao_devis_one'),
    path('ao/delete_devis/<int:id>/', views.ao_delete_devis, name='ao_delete_devis'),

    ## Parametres ##

    path('ao/parametres/', views.ao_parametres, name='ao_parametres'),
    path('ao/delete_tva/<int:id>/', views.ao_delete_tva, name='ao_delete_tva'),
    path('ao/add_tva/', views.ao_add_tva, name='ao_add_tva'),





    ####  Elearning ####

    path('elearning/general_view/', views.elearning_general_view, name='elearning_general_view'),


    # Demandes Professeurs
    path('elearning/demandes_professeurs/', views.elearning_demandes_professeurs, name='elearning_demandes_professeurs'),
    path('elearning/delete_demandes_professeurs/', views.elearning_delete_demandes_professeurs, name='elearning_delete_demandes_professeurs'),
    path('elearning/approve_shops/', views.elearning_approve_demandes_professeurs, name='elearning_approve_demandes_professeurs'),

    # Professeurs
    path('elearning/professeurs/', views.elearning_professeurs, name='elearning_professeurs'),
    path('elearning/delete_statut_professeur/', views.elearning_delete_statut_professeur, name='elearning_delete_statut_professeur'),

    # Categories
    path('elearning/categories/', views.elearning_categories, name='elearning_categories'),

    path('elearning/add_category/', views.elearning_add_category, name='elearning_add_category'),
    path('elearning/delete_categories/', views.elearning_delete_categories, name='elearning_delete_categories'),
    path('elearning/delete_category/<int:id_category>/', views.elearning_delete_category, name='elearning_delete_category'),
    path('elearning/update_category/<int:id_category>/', views.elearning_update_category, name='elearning_update_category'),

    # Sous Categories
    path('elearning/sub_categories/', views.elearning_sub_categories, name='elearning_sub_categories'),

    path('elearning/add_sub_category/', views.elearning_add_sub_category, name='elearning_add_sub_category'),
    path('elearning/delete_sub_categories/', views.elearning_delete_sub_categories, name='elearning_delete_sub_categories'),
    path('elearning/delete_sub_category/<int:id_category>/', views.elearning_delete_sub_category,
         name='elearning_delete_sub_category'),
    path('elearning/update_sub_category/<int:id_category>/', views.elearning_update_sub_category,
         name='elearning_update_sub_category'),

    # Cours
    path('elearning/cours/', views.elearning_cours, name='elearning_cours'),
    path('elearning/delete_cours/', views.elearning_delete_cours, name='elearning_delete_cours'),
    path('elearning/approve_cours/', views.elearning_approve_cours, name='elearning_approve_cours'),
    path('elearning/deapprove_cours/', views.elearning_deapprove_cours, name='elearning_deapprove_cours'),
    path('elearning/active_cours/', views.elearning_active_cours, name='elearning_active_cours'),
    path('elearning/deactive_cours/', views.elearning_deactive_cours, name='elearning_deactive_cours'),

    path('elearning/cours/<int:id>', views.elearning_infos_cours, name='elearning_infos_cours'),

    path('elearning/delete_cours/<int:id>/', views.elearning_delete_cours, name='elearning_delete_cours'),
    path('elearning/update_cours/<int:id>/', views.elearning_update_cours,  name='elearning_update_cours'),

    #Pre_requis
    path('elearning/cours/<int:id>/add_prerequis/', views.elearning_add_prerequis, name='elearning_add_prerequis'),
    path('elearning/delete_prerequis/<int:id_prerequis>/', views.elearning_delete_prerequis, name='elearning_delete_prerequis'),
    path('elearning/update_prerequis/<int:id_prerequis>/', views.elearning_update_prerequis, name='elearning_update_prerequis'),

    # Post Skills
    path('elearning/cours/<int:id>/add_postskill/', views.elearning_add_postskill, name='elearning_add_postskill'),
    path('elearning/delete_postskill/<int:id_postskill>/', views.elearning_delete_postskill, name='elearning_delete_postskill'),
    path('elearning/update_postskill/<int:id_postskill>/', views.elearning_update_postskill,  name='elearning_update_postskill'),

    # Chapitre
    path('elearning/cours/<int:id>/add_chapter/', views.elearning_add_chapter, name='elearning_add_chapter'),
    path('elearning/delete_chapter/<int:id_chapter>/', views.elearning_delete_chapter,   name='elearning_delete_chapter'),
    path('elearning/update_chapter/<int:id_chapter>/', views.elearning_update_chapter,  name='elearning_update_chapter'),

    # Leçon
    path('elearning/chapter/<int:id_chapitre>/add_lecon/', views.elearning_add_lecon, name='elearning_add_lecon'),
    path('elearning/delete_lecon/<int:id_lecon>/', views.elearning_delete_lecon, name='elearning_delete_lecon'),
    path('elearning/update_lecon/<int:id_lecon>/', views.elearning_update_lecon, name='elearning_update_lecon'),

    # Coupons
    path('elearning/coupons/', views.elearning_coupons, name='elearning_coupons'),

    path('elearning/add_coupon/', views.elearning_add_coupon, name='elearning_add_coupon'),
    path('elearning/delete_coupons/', views.elearning_delete_coupons,
         name='elearning_delete_coupons'),
    path('elearning/delete_coupon/<int:id>/', views.elearning_delete_coupon,
         name='elearning_delete_coupon'),
    path('elearning/update_coupon/<int:id>/', views.elearning_update_coupon,
         name='elearning_update_coupon'),

    # Promotions
    path('elearning/sales/', views.elearning_sales, name='elearning_sales'),

    path('elearning/add_sales/', views.elearning_add_sales, name='elearning_add_sales'),
    path('elearning/delete_sales/', views.elearning_delete_sales,
         name='elearning_delete_sales'),
    path('elearning/delete_sales/<int:id>/', views.elearning_delete_sale,
         name='elearning_delete_sale'),
    path('elearning/update_sales/<int:id>/', views.elearning_update_sales,
         name='elearning_update_sales'),

    # Commandes
    path('elearning/orders/', views.elearning_orders, name='elearning_orders'),

    path('elearning/order/<int:id>/', views.elearning_order, name='elearning_order'),
    path('elearning/delete_orders/', views.elearning_delete_orders,  name='elearning_delete_orders'),
    path('elearning/delete_order/<int:id>/', views.elearning_delete_order, name='elearning_delete_order'),

    ################################    Autres Liens    ################################
    path('test/', views.test, name='test'),
    path('', views.index, name='index'),
    path('logout/', views.logout, name='logout'),


]
