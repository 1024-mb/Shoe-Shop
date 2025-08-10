from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from . import views



urlpatterns = [
    path('', views.activity, name='activity'),
    path('update_details/', views.user_profile, name='user_profile'),
    path('order/<str:pk>', views.order, name='order'),

]