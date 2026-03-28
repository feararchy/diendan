from django.urls import path
from . import views

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
]