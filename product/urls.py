from django.urls import path
from . import views


urlpatterns = [
    path('<str:pk>', views.product, name='product'),
    path('', views.product, name='product'),
    path('<str:pk>/create_review/', views.create_review, name='create_review'),
    
   path('<str:pk>/update_review/', views.update_review, name='update_review'),

    path('<str:pk>/delete_review/', views.delete_review, name='delete_review'),
]