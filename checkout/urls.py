from django.urls import path, include
from . import views
import djstripe

"""
    path('', include('djstripe.urls', namespace='djstripe')),
    path('stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),
    """

urlpatterns = [
    path('', views.checkout, name='checkout'),

    path('payment_processing/', views.payment_processing, name='payment_processing'),
    path('get_order_status/', views.get_order_status, name='get_order_status'),

    path('payment_succeeded/', views.payment_succeeded, name='payment_succeeded'),
    path('payment_failed/', views.payment_failed, name='payment_failed'),    
]