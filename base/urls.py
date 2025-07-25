from django.urls import path, include
from django.shortcuts import redirect
from . import views

def redirect_to_home(request):
    
    return redirect('home', permanent=True)


urlpatterns = [
    path('', redirect_to_home),
    path('home/',  views.home, name='home'),

    path('login/', views.login_page, name='login'),
    path('register/', views.register, name='register'),
    
    path('lougout/', views.Logout, name='logout'),

    path('profile/', views.user_profile, name='profile')
]