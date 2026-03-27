from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('topic/new/', views.create_topic, name='create_topic'),
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    
    # Link tài khoản
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
]