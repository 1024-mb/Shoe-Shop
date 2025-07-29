from django.urls import path
from . import views


urlpatterns = [
    path('', views.cart, name='cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
]
