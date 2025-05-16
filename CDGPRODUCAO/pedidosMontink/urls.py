from django.urls import path
from .views import WebhookReceiverView, WebhookStatusView

urlpatterns = [
    path('receber/', WebhookReceiverView.as_view(), name='webhook-receiver'),
    path('status/<int:pedido_id>/', WebhookStatusView.as_view(), name='status-change'),
]
