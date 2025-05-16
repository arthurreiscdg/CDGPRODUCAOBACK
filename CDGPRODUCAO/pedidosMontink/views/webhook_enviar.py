from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..services.webhook_service import WebhookService
from ..services.pedido_service import PedidoService
from ..serializers.pedido_serializers import PedidoModelSerializer
import json



class WebhookStatusView(APIView):
    """
    Endpoint para atualizar o status de um pedido e enviar webhook.
    """

    def post(self, request, pedido_id):
        # Verifica se o pedido existe
        pedido = PedidoService.obter_pedido(pedido_id)
        if not pedido:
            return Response(
                {'error': f'Pedido com ID {pedido_id} não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Obtém o novo status do pedido
        novo_status = request.data.get('status')
        if not novo_status:
            return Response(
                {'error': 'O campo "status" é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Atualiza o status
        pedido, status_obj, webhooks_enviados = PedidoService.alterar_status(
            pedido_id=pedido_id,
            novo_status_nome=novo_status,
            enviar_webhook=True
        )
        
        # Prepara a resposta
        serializer = PedidoModelSerializer(pedido)
        return Response({
            'message': f'Status alterado para: {novo_status}',
            'pedido': serializer.data,
            'webhooks_enviados': len(webhooks_enviados),
        }, status=status.HTTP_200_OK)
