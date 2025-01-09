from django.urls import path
from . import views

urlpatterns = [
    path('',views.introduction,name='introduction'),
    path('chatbot', views.chatbot, name='chatbot'),
    path('chatbot1',views.chatbot1,name='chatbot1'),
    path('user_login', views.login, name='user_login'),
    path('register', views.register, name='register'),
    path('user_logout', views.logout, name='user_logout'),
    path('dashbord',views.dashbord,name='dashbord'),
    path('chathistory',views.chathistory,name='chathistory'),
    path('settings',views.settings,name='settings'),
    
]