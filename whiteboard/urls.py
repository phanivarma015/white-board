# urls.py

from django.contrib import admin
from django.urls import path
from boardapp import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.login, name="login"),
    path('login/', views.login, name="login"),
    path('signup/', views.signup, name="signup"),
    path('home/', views.home, name="home"),

    path('create-meeting/', views.create_meeting, name="create_meeting"),
    path('meeting/<str:room_name>/', views.meeting_room, name="meeting_room"),
    path('delete-meeting/<str:room_name>/', views.delete_meeting, name="delete_meeting"),
]