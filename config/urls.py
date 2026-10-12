from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from remote import views
urlpatterns = [path('', views.dashboard, name='dashboard'), path('command/<str:action>/', views.command, name='command'), path('login/', LoginView.as_view(template_name='remote/login.html'), name='login'), path('logout/', LogoutView.as_view(), name='logout')]
