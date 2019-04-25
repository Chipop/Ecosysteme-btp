from django.urls import path

from qa import views

app_name = 'qa'

urlpatterns = [
    path('', views.index, name='home'),
    path('question/<int:qst_id>/', views.question_detail, name='question'),
    path('question/<int:qst_id>/answer/', views.add_answer, name='answer'),
    path('like/<int:selected_answer>/', views.like, name='like'),
    path('question/category/<int:category_id>/', views.category, name='category'),
    path('question/all/', views.all_questions, name='all_questions'),
    path('question/add/', views.add_question, name='add_question'),
    path('question/<int:qst_id>/delete/', views.delete_question, name='delete_question'),
    path('question/<int:qst_id>/<int:answer_id>/delete/', views.delete_answer, name='delete_answer'),
    path('profile/<int:profile_id>/', views.profile, name='profile'),
    path('profile/<int:profile_id>/update/', views.update_profile, name='update_profile'),
    path('profile/<int:profile_id>/notifications/', views.notification, name='notification'),
    path('profile/<int:profile_id>/notifications/all', views.all_notification_open, name='all_notification_open'),
    path('profile/<int:profile_id>/notifications/<int:n_id>/', views.notification_open, name='notification_open'),
    path('blog/', views.blog, name='blog'),
    path('blog/category/<int:category_id>/', views.blog_category, name='blog_category'),
    path('blog/tag/<int:tag_id>/', views.blog_tag, name='blog_tag'),
    path('blog/article/<int:article_id>/', views.blog_post, name='blog_post'),
    path('blog/<int:post_id>/like/', views.like_post, name='like_post'),
    path('blog/post/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('blog/<int:article_id>/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('blog/<int:article_id>/delete/', views.delete_post, name='delete_post'),
    path('blog/article/add/', views.add_post, name='add_post'),
    path('blog/article/update/<int:article_id>/', views.update_post, name='update_post'),
    path('how-it-work/', views.how_it_work, name='how_it_work'),
    path('contact/', views.contact, name='contact',),

    # Signal Urls
    path('question/<int:qst_id>/signal/', views.signal_question, name='signal_question'),
    path('question/<int:qst_id>/answer/<int:answer_id>/signal/', views.signal_answer, name='signal_answer'),
    path('blog/article/<int:article_id>/signal/', views.signal_article, name='signal_article'),
    path('blog/article/<int:article_id>/comment/<int:comment_id>/signal/', views.signal_comment, name='signal_comment'),

    # Shares
    path('question/share/<int:id>/', views.share_question, name='share_question'),
    path('article/share/<int:id>/', views.share_article, name='share_article'),

]
