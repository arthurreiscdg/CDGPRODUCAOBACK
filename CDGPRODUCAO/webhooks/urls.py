from django.urls import path, include
from rest_framework.routers import DefaultRouter
from webhooks.views import (
    WebhookReceiverView,
    WebhookSenderView,
    WebhookEndpointConfigView,
    PedidoViewSet
)

# Configurar o router para o ViewSet de pedidos
router = DefaultRouter()
router.register(r'pedidos', PedidoViewSet)

urlpatterns = [
    # URLs para receber webhooks
    path('receive/', WebhookReceiverView.as_view(), name='webhook-receive'),
    
    # URLs para enviar webhooks
    path('send/', WebhookSenderView.as_view(), name='webhook-send'),
    
    # URLs para gerenciar configurações de endpoints
    path('endpoints/', WebhookEndpointConfigView.as_view(), name='webhook-endpoints'),
    
    # Incluir as URLs do router
    path('', include(router.urls)),
]
