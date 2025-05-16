import json
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from webhooks.services import WebhookProcessor
from webhooks.models import Pedido
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
            
            # Se o webhook for um pedido, cria um novo registro de pedido
            pedido = None
            if event_type == 'novo_pedido' or event_type == 'pedido_atualizado':
                try:
                    pedido = Pedido.criar_do_webhook(webhook)
                    logger.info(f"Pedido #{pedido.numero_pedido} criado/atualizado com sucesso a partir do webhook")
                except Exception as e:
                    logger.error(f"Erro ao criar pedido a partir do webhook: {str(e)}")
            
            # Retorna a resposta
            serializer = WebhookSerializer(webhook)
            response_data = {
                'status': 'success',
                'message': 'Webhook recebido com sucesso',
                'webhook': serializer.data
            }
            
            if pedido:
                response_data['pedido_criado'] = True
                response_data['numero_pedido'] = pedido.numero_pedido
            
            return Response(response_data, status=status.HTTP_200_OK)
            
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