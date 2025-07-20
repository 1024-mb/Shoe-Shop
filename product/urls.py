from django.urls import path
from . import views


urlpatterns = [
    path('<str:pk>', views.product, name='product'),
    path('', views.product, name='product'),
    path('<str:pk>/add_review/', views.create_review, name='add_review')
]