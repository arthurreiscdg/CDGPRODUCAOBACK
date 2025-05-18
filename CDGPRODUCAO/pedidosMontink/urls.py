from django.urls import path
from .views.webhook_receber import WebhookReceberView
from .views.pedido_listar import WebhookListarView, StatusPedidoListView, PedidoDetailView, AtualizarStatusPedidoView

urlpatterns = [
    path('receber/', WebhookReceberView.as_view(), name='webhook-receiver'),
    path('pedidos/', WebhookListarView.as_view(), name='pedidos-listar'),
    path('pedidos/<int:pk>/', PedidoDetailView.as_view(), name='pedido-detalhe'),
    path('pedidos/<int:pk>/status/', AtualizarStatusPedidoView.as_view(), name='pedido-atualizar-status'),
    path('pedidos/status/', StatusPedidoListView.as_view(), name='pedidos-status'),
]
