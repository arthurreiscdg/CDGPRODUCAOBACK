from django.urls import path
from webhooks.views import (
    WebhookReceiverView,
    WebhookSenderView,
    WebhookEndpointConfigView
)

urlpatterns = [
    # URLs para receber webhooks
    path('receive/', WebhookReceiverView.as_view(), name='webhook-receive'),
    
    # URLs para enviar webhooks
    path('send/', WebhookSenderView.as_view(), name='webhook-send'),
    
    # URLs para gerenciar configurações de endpoints
    path('endpoints/', WebhookEndpointConfigView.as_view(), name='webhook-endpoints'),
]
