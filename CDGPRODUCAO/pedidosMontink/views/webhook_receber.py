from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..services.webhook_service import WebhookService
from ..services.pedido_service import PedidoService
from ..serializers.pedido_serializers import PedidoModelSerializer
import json


class WebhookReceiverView(APIView):
    """
    Endpoint para receber webhooks com dados de pedidos da plataforma Montink.
    
    Este endpoint processa webhooks com a estrutura de dados definida abaixo:
    ```
    {
        "valor_pedido": FLOAT,
        "custo_envio": FLOAT,
        "etiqueta_envio": STRING,
        "metodo_envio": INT,
        "numero_pedido": INT,
        "nome_cliente": STRING,
        "documento_cliente": STRING,
        "email_cliente": STRING,
        "produtos": [
            {
                "nome": STRING,
                "sku": STRING,
                "quantidade": INT,
                "id_sku": INT,
                "designs": {
                    "capa_frente": STRING,
                    "capa_verso": STRING
                },
                "mockups": {
                    "capa_frente": STRING,
                    "capa_costas": STRING
                },
                "arquivo_pdf": STRING
            }
        ],
        "informacoes_adicionais": {
            "nome": STRING,
            "telefone": STRING,
            "email": STRING
        },
        "endereco_envio": {
            "nome_destinatario": STRING,
            "endereco": STRING,
            "numero": STRING,
            "complemento": STRING,
            "cidade": STRING,
            "uf": STRING,
            "cep": STRING,
            "bairro": STRING,
            "telefone": STRING,
            "pais": STRING
        }
    }
    ```
    """

    def post(self, request):
        """
        Recebe e processa um webhook de pedido.
        
        A assinatura do webhook deve ser enviada no cabeçalho 'X-Webhook-Signature'.
        """
        # Obtém a assinatura do cabeçalho
        assinatura = request.headers.get('X-Webhook-Signature')
        
        # Obtém o payload e decodifica
        payload = request.body.decode('utf-8')
        
        try:
            # Verifica se o payload é um JSON válido
            json_data = json.loads(payload)
            
            # Valida campos obrigatórios mínimos
            campos_obrigatorios = ['numero_pedido', 'valor_pedido', 'produtos']
            for campo in campos_obrigatorios:
                if campo not in json_data:
                    return Response(
                        {'error': f'Campo obrigatório ausente: {campo}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Verifica se há pelo menos um produto
            if not json_data.get('produtos') or not isinstance(json_data['produtos'], list) or len(json_data['produtos']) == 0:
                return Response(
                    {'error': 'É necessário pelo menos um produto no pedido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Processa o webhook
            webhook, pedido, verificado = WebhookService.processar_webhook(
                payload=payload,
                assinatura=assinatura,
                evento='pedido'
            )
            
            # Verifica o resultado do processamento
            if assinatura and not verificado:
                return Response(
                    {'error': 'Assinatura inválida ou secret key incorreta'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Se o processamento criou um pedido, retorna seus dados
            if pedido:
                serializer = PedidoModelSerializer(pedido)
                return Response(
                    {
                        'message': 'Webhook recebido e processado com sucesso',
                        'pedido': serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            
            # Caso contrário, apenas confirma o recebimento
            return Response(
                {'message': 'Webhook recebido, mas não foi possível criar um pedido'},
                status=status.HTTP_200_OK
            )
            
        except json.JSONDecodeError:
            return Response(
                {'error': 'Payload inválido. Formato JSON esperado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Em um ambiente de produção, seria importante registrar o erro em um sistema de logs
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao processar webhook: {str(e)}", exc_info=True)
            
            return Response(
                {'error': f'Erro ao processar webhook: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )