from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('register/', views.registerPage, name='register'),

    path('', views.home, name='home'),
    path('profile/<str:pk>/', views.userProfile, name='user-profile'),
    path('update-user/', views.updateUser, name='update-user'),
    
    path('room/<str:pk>', views.room, name='room'),
    path('create_room/', views.createRoom, name='create-room'),
    path('update_room/<str:pk>', views.updateRoom, name='update-room'),
    path('delete_room/<str:pk>', views.deleteRoom, name='delete-room'),
    path('delete_message/<str:pk>', views.deleteMessage, name='delete-msg'),

    path('topics/', views.topicPage, name='topics'),
    path('activity/', views.activityPage, name='activity'),
]