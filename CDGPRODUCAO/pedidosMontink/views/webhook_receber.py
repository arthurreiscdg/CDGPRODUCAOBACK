from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from pedidosMontink.services.webhook_service import WebhookService
from pedidosMontink.serializers.webhook_serializers import (
    WebhookPedidoRequestSerializer, 
    WebhookPedidoResponseSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class WebhookReceberView(APIView):
    """
    View para receber webhooks de pedidos.
    
    Esta view recebe os dados de pedidos enviados por sistemas externos,
    verifica se a assinatura é válida usando a secret_key configurada, 
    e salva o pedido na base de dados.
    """
    def post(self, request, *args, **kwargs):
        """
        Recebe um webhook com dados de pedido.
        
        A requisição deve conter um payload JSON com os dados do pedido.
        Se a assinatura estiver configurada, deve ser enviada no header 'X-Signature'.
        """
        # Pegar a assinatura se estiver presente no header
        assinatura = request.headers.get('X-Signature')
        
        # Manter o payload bruto para verificação da assinatura
        payload_raw = request.body
          # Validar o formato do JSON recebido
        try:
            dados = json.loads(payload_raw.decode('utf-8'))
            serializer = WebhookPedidoRequestSerializer(data=dados)
            
            if not serializer.is_valid():
                # Criar um registro de webhook com erro de validação
                from pedidosMontink.models import Webhook
                erro_str = json.dumps(serializer.errors)
                
                Webhook.objects.create(
                    evento='erro.validacao',
                    payload=payload_raw.decode('utf-8'),
                    assinatura=assinatura,
                    verificado=False,
                    status_code=400,
                    erro=f"Formato de dados inválido: {erro_str}",
                    processado=False
                )
                
                return Response({
                    'sucesso': False,
                    'mensagem': 'Formato de dados inválido',
                    'erros': serializer.errors,
                    'pedido_id': None
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except json.JSONDecodeError:
            # Criar um registro de webhook com erro de JSON inválido
            from pedidosMontink.models import Webhook
            
            Webhook.objects.create(
                evento='erro.json',
                payload=payload_raw.decode('utf-8', errors='replace'),  # Usar replace para lidar com caracteres inválidos
                assinatura=assinatura,
                verificado=False,
                status_code=400,
                erro="Payload inválido: não é um JSON válido",
                processado=False
            )
            
            return Response({
                'sucesso': False,
                'mensagem': 'Payload inválido: não é um JSON válido',
                'pedido_id': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Processar o webhook
        sucesso, mensagem, pedido_id = WebhookService.processar_webhook_pedido(
            payload_raw=payload_raw, 
            assinatura_recebida=assinatura
        )
        
        # Preparar a resposta
        resposta = {
            'sucesso': sucesso,
            'mensagem': mensagem,
            'pedido_id': pedido_id
        }
          # Serializar e retornar a resposta
        serializer = WebhookPedidoResponseSerializer(data=resposta)
        serializer.is_valid(raise_exception=True)
        
        codigo_status = status.HTTP_201_CREATED if sucesso else status.HTTP_400_BAD_REQUEST
        
        # Certifique-se de atualizar o registro do webhook se ainda não foi feito
        from pedidosMontink.models import Webhook
        try:
            webhook = Webhook.objects.filter(payload=payload_raw.decode('utf-8')).order_by('-recebido_em').first()
            if webhook and webhook.status_code is None:
                webhook.status_code = codigo_status
                webhook.processado = sucesso
                if not sucesso and not webhook.erro:
                    webhook.erro = mensagem
                webhook.save()
        except Exception:
            pass  # Se não conseguir atualizar o webhook, apenas continue
        
        return Response(serializer.data, status=codigo_status)