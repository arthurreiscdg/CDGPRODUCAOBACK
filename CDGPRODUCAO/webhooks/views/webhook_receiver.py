import json
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from webhooks.services import WebhookProcessor
from webhooks.serializers import WebhookSerializer

logger = logging.getLogger(__name__)

class WebhookReceiverView(APIView):
    """
    View para receber webhooks de sistemas externos.
    
    Esta view aceita POSTs com payloads de webhook, verifica a assinatura
    e processa o webhook recebido.
    """
    permission_classes = [AllowAny]  # Permite requisições sem autenticação
    
    def post(self, request, *args, **kwargs):
        try:
            # Extrai as informações da requisição
            payload = request.body.decode('utf-8')
            event_type = request.headers.get('X-Webhook-Event', 'unknown')
            signature = request.headers.get('X-Webhook-Signature')
            
            # Processa o webhook
            webhook = WebhookProcessor.process_webhook(
                evento=event_type,
                payload=payload,
                signature=signature
            )
            
            # Retorna a resposta
            serializer = WebhookSerializer(webhook)
            return Response(
                {
                    'status': 'success',
                    'message': 'Webhook recebido com sucesso',
                    'webhook': serializer.data
                },
                status=status.HTTP_200_OK
            )
            
        except json.JSONDecodeError:
            logger.error("Payload inválido: não é um JSON válido")
            return Response(
                {'status': 'error', 'message': 'Payload inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            return Response(
                {'status': 'error', 'message': f'Erro ao processar webhook: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )