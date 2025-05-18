from django.urls import path
from .views.webhook_receber import WebhookReceberView
from .views.webhook_listar import WebhookListarView, StatusPedidoListView

urlpatterns = [
    path('receber/', WebhookReceberView.as_view(), name='webhook-receiver'),
    path('pedidos/', WebhookListarView.as_view(), name='pedidos-listar'),
    path('pedidos/status/', StatusPedidoListView.as_view(), name='pedidos-status'),
]
