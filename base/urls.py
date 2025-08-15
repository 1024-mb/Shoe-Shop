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
    path('confirm_email/', views.confirm_email, name='confirm_email'),

    path('logout/', views.logout_page, name='logout'),

    path('profile/', include('user_profile.urls'), name='profile'),

    path('reset_password/', views.reset_password, name='reset_password'),

    path('enter_code/', views.enter_code, name='enter_code'),

    path('set_password/', views.set_password, name='set_password'),

    path('stripe/webhook', views.stripe_webhook, name='stripe_webhook')
]