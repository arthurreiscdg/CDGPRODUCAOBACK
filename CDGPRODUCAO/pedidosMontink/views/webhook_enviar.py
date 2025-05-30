# filepath: c:\Users\Arthur Reis\Documents\PROJETOCASADAGRAFICA\CDGPRODUCAOBACK\CDGPRODUCAO\pedidosMontink\views\webhook_enviar.py
import json
import requests
import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models.webhook_config import WebhookEndpointConfig, WebhookStatusEnviado
from ..models.webhook_pedido import Pedido, StatusPedido
from ..serializers.pedido_serializers import PedidoSerializer
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


class WebhookService:
    @staticmethod
    def enviar_webhook_status(pedido, novo_status, old_status=None, atualizar_pedido=True):
        """
        Envia webhooks para todos os endpoints configurados 
        quando um pedido muda de status
        
        Args:
            pedido: O objeto Pedido que teve o status alterado
            novo_status: O objeto StatusPedido novo
            old_status: O objeto StatusPedido anterior (opcional)
            atualizar_pedido: Se True, atualiza o status do pedido automaticamente após enviar os webhooks.
                              Se False, não atualiza o status do pedido.
        
        Returns:
            list: Lista de WebhookStatusEnviado com os resultados dos envios
        """
        # Obter todos os endpoints ativos
        endpoints = WebhookEndpointConfig.objects.filter(ativo=True, auto_enviar=True)
        resultados = []
        
        if not endpoints.exists():
            logger.warning("Nenhum endpoint de webhook configurado ou ativo")
            
            # Se não há endpoints e atualizar_pedido=True, atualiza o pedido
            if atualizar_pedido:
                pedido.status = novo_status
                pedido.save(update_fields=['status', 'atualizado_em'])
                logger.info(f"Status do pedido #{pedido.id} alterado para {novo_status.nome} sem webhooks")
                
            return resultados        # Preparar payload no formato solicitado
        payload = {
            "data": pedido.atualizado_em.isoformat(),
            "access_token": "",  # Valor inicial vazio que será substituído para cada endpoint
            "json": {
                "casa_grafica_id": str(pedido.numero_pedido),  # Usando o número do pedido conforme solicitado
                "status_id": novo_status.id,
                "status": novo_status.nome
            }
        }
        
        # O access_token correto será definido individualmente para cada endpoint
            
        payload_json = json.dumps(payload)
        
        # Enviar para cada endpoint configurado
        for endpoint in endpoints:
            try:                # Preparar URL sem anexar token como parâmetro
                url = endpoint.url
                
                # Preparar headers
                headers = {
                    'Content-Type': 'application/json',
                }
                
                if endpoint.token_autenticacao:
                    headers['Authorization'] = f'Bearer {endpoint.token_autenticacao}'
                
                # Adicionar headers adicionais se configurados
                if endpoint.headers_adicionais:
                    try:
                        headers_adicionais = json.loads(endpoint.headers_adicionais)
                        headers.update(headers_adicionais)
                    except json.JSONDecodeError:
                        logger.error(f"Headers adicionais inválidos para o endpoint {endpoint.nome}")
                  # Adicionar o access_token ao payload específico para este endpoint
                # Vamos reconstruir o payload para garantir a ordem correta dos campos
                token_value = endpoint.access_token if endpoint.access_token else ""
                
                # Criando um novo dicionário com a ordem correta dos campos (data, access_token, json)
                endpoint_payload = {
                    "data": pedido.atualizado_em.isoformat(),
                    "access_token": token_value,
                    "json": {
                        "casa_grafica_id": str(pedido.numero_pedido),
                        "status_id": novo_status.id,
                        "status": novo_status.nome
                    }
                }
                
                # Converter o payload com o token incluído para JSON
                endpoint_payload_json = json.dumps(endpoint_payload)
                
                # Enviar requisição com o payload específico para este endpoint
                response = requests.post(url, data=endpoint_payload_json, headers=headers, timeout=10)
                  # Registrar resultado
                webhook_enviado = WebhookStatusEnviado.objects.create(
                    pedido=pedido,
                    status=novo_status.nome,
                    url_destino=url,
                    payload=endpoint_payload_json,  # Usando o payload específico do endpoint com access_token
                    resposta=response.text[:1000],  # Limitamos o tamanho da resposta
                    codigo_http=response.status_code,
                    sucesso=response.ok
                )
                
                resultados.append(webhook_enviado)
                
                logger.info(f"Webhook enviado para {endpoint.nome}, status: {response.status_code}")
                
                if not response.ok:
                    logger.warning(f"Falha ao enviar webhook: {response.text[:200]}")
                
            except Exception as e:
                logger.error(f"Erro ao enviar webhook para {endpoint.nome}: {str(e)}")
                  # Registrar falha
                # Tentar usar o payload específico do endpoint se disponível, senão usar o payload original
                payload_to_save = endpoint_payload_json if 'endpoint_payload_json' in locals() else payload_json
                
                webhook_enviado = WebhookStatusEnviado.objects.create(
                    pedido=pedido,
                    status=novo_status.nome,
                    url_destino=url if 'url' in locals() else endpoint.url,
                    payload=payload_to_save,
                    resposta=str(e),
                    sucesso=False
                )
                
                resultados.append(webhook_enviado)
        
        # Depois de enviar todos os webhooks, atualiza o status do pedido se solicitado
        if atualizar_pedido:
            # Verificar se todos os webhooks foram enviados com sucesso
            falhas = sum(1 for r in resultados if not r.sucesso)
            if falhas == 0:
                # Atualiza o status apenas se não houve falhas
                pedido.status = novo_status
                pedido.save(update_fields=['status', 'atualizado_em'])
                logger.info(f"Status do pedido #{pedido.id} alterado para {novo_status.nome} após webhooks bem-sucedidos")
            else:
                logger.error(f"Status do pedido #{pedido.id} NÃO foi alterado devido a {falhas} falhas em webhooks")
                
        return resultados


class EnviarWebhookManualView(APIView):
    """
    View para enviar manualmente webhooks de status para um pedido
    """
    def post(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        try:
            resultados = WebhookService.enviar_webhook_status(
                pedido=pedido,
                novo_status=pedido.status
            )
            
            # Contar sucessos e falhas
            sucessos = sum(1 for r in resultados if r.sucesso)
            falhas = len(resultados) - sucessos
            
            return Response({
                "mensagem": f"Webhooks enviados: {len(resultados)} (sucessos: {sucessos}, falhas: {falhas})",
                "resultados": [{
                    "endpoint": r.url_destino,
                    "status": r.codigo_http,
                    "sucesso": r.sucesso
                } for r in resultados]
            })
            
        except Exception as e:
            return Response(
                {"erro": f"Erro ao enviar webhook: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
