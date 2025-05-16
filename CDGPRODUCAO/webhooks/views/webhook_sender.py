import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from webhooks.models import WebhookEndpointConfig
from webhooks.serializers import WebhookEndpointConfigSerializer, WebhookStatusEnviadoSerializer
from webhooks.services import WebhookSender

logger = logging.getLogger(__name__)

class WebhookSenderView(APIView):
    """
    View para enviar webhooks para endpoints externos.
    
    Esta view permite enviar webhooks manualmente para endpoints configurados.
    Requer autenticação.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            # Valida os parâmetros obrigatórios
            pedido_id = request.data.get('pedido_id')
            status_pedido = request.data.get('status')
            payload = request.data.get('payload')
            endpoint_id = request.data.get('endpoint_id')
            
            if not all([pedido_id, status_pedido, payload]):
                return Response(
                    {
                        'status': 'error', 
                        'message': 'Os campos pedido_id, status e payload são obrigatórios'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Busca o endpoint configurado se especificado
            endpoint = None
            if endpoint_id:
                try:
                    endpoint = WebhookEndpointConfig.objects.get(id=endpoint_id, ativo=True)
                except WebhookEndpointConfig.DoesNotExist:
                    return Response(
                        {'status': 'error', 'message': f'Endpoint com ID {endpoint_id} não encontrado ou inativo'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Envia o webhook
            success, http_code, response_text, webhook_status = WebhookSender.send_webhook(
                pedido_id=pedido_id,
                status=status_pedido,
                payload_data=payload,
                endpoint_config=endpoint
            )
            
            # Retorna o resultado
            serializer = WebhookStatusEnviadoSerializer(webhook_status)
            return Response({
                'status': 'success' if success else 'error',
                'message': 'Webhook enviado com sucesso' if success else 'Falha ao enviar webhook',
                'webhook_status': serializer.data
            }, status=status.HTTP_200_OK if success else status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Erro ao enviar webhook: {str(e)}")
            return Response(
                {'status': 'error', 'message': f'Erro ao enviar webhook: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WebhookEndpointConfigView(APIView):
    """
    View para gerenciar configurações de endpoints de webhook.
    
    Esta view permite listar e criar configurações de endpoints.
    Requer autenticação.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Lista todas as configurações de endpoints."""
        endpoints = WebhookEndpointConfig.objects.all()
        serializer = WebhookEndpointConfigSerializer(endpoints, many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        """Cria uma nova configuração de endpoint."""
        serializer = WebhookEndpointConfigSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)