from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('', views.home, name='home'),
    path('topic/new/', views.create_topic, name='create_topic'),
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    # profile
    path('topic/<int:topic_id>/like/', views.like_topic, name='like_topic'),
    path('topic/<int:topic_id>/delete/', views.delete_topic, name='delete_topic'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('topic/<int:topic_id>/edit/', views.edit_topic, name='edit_topic'),
    path('category/<int:category_id>/', views.category_topics, name='category_topics'),
    path('members/', views.members_list, name='members_list'),
    # Link tài khoản
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
        # JSON API endpoints
    path("api/docs/", api_views.api_docs, name="api_docs"),
    path("api/health/", api_views.api_health, name="api_health"),
    path("api/categories/", api_views.api_categories, name="api_categories"),
    path("api/topics/", api_views.api_topics, name="api_topics"),
    path("api/topics/<int:topic_id>/", api_views.api_topic_detail, name="api_topic_detail"),
    path("api/auth/login/", api_views.api_login, name="api_login"),
    path("api/auth/me/", api_views.api_me, name="api_me"),
    path("api/topics/<int:topic_id>/like/", api_views.api_like_topic, name="api_like_topic"),
]