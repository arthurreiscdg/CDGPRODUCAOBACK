from django.urls import path
from .views.webhook_receber import WebhookReceberView

urlpatterns = [
    path('receber/', WebhookReceberView.as_view(), name='webhook-receiver'),
]
