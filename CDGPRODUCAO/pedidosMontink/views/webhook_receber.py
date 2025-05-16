from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..services.webhook_service import WebhookService
from ..services.pedido_service import PedidoService
from ..serializers.pedido_serializers import PedidoModelSerializer
import json


class WebhookReceiverView(APIView):
    """
    Endpoint para receber webhooks com dados de pedidos.
    """

    def post(self, request):
        # Obtém a assinatura do cabeçalho
        assinatura = request.headers.get('X-Webhook-Signature')
        
        # Obtém o payload e serializa
        payload = request.body.decode('utf-8')
        
        try:
            # Processa o webhook
            webhook, pedido, verificado = WebhookService.processar_webhook(
                payload=payload,
                assinatura=assinatura,
                evento='pedido'
            )
            
            # Verifica o resultado do processamento
            if assinatura and not verificado:
                return Response(
                    {'error': 'Assinatura inválida'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Se o processamento criou um pedido, retorna seus dados
            if pedido:
                serializer = PedidoModelSerializer(pedido)
                return Response(
                    {'message': 'Webhook recebido e processado com sucesso', 'pedido': serializer.data},
                    status=status.HTTP_201_CREATED
                )
            
            # Caso contrário, apenas confirma o recebimento
            return Response(
                {'message': 'Webhook recebido'},
                status=status.HTTP_200_OK
            )
            
        except json.JSONDecodeError:
            return Response(
                {'error': 'Payload inválido. Formato JSON esperado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Log do erro seria útil aqui
            return Response(
                {'error': f'Erro ao processar webhook: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )