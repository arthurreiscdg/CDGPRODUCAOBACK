import hashlib
import hmac
import json
import logging
import requests
from typing import Dict, Any, Optional, Tuple

from django.conf import settings
from webhooks.models import Webhook, WebhookConfig, WebhookEndpointConfig, WebhookStatusEnviado

logger = logging.getLogger(__name__)

class WebhookProcessor:
    """
    Classe responsável pelo processamento de webhooks recebidos.
    """
    
    @staticmethod
    def verify_webhook(payload: str, signature: str) -> bool:
        """
        Verifica a assinatura de um webhook usando HMAC-SHA256.
        
        Args:
            payload: O payload do webhook em formato de string.
            signature: A assinatura do webhook fornecida pelo remetente.
            
        Returns:
            bool: True se a assinatura for válida, False caso contrário.
        """
        try:
            # Busca a configuração ativa de webhook
            config = WebhookConfig.objects.filter(ativo=True).first()
            if not config:
                logger.warning("Nenhuma configuração de webhook ativa encontrada")
                return False
                
            # Calcula o HMAC usando a chave secreta
            secret = config.secret_key.encode('utf-8')
            payload_bytes = payload.encode('utf-8')
            
            calculated_hmac = hmac.new(
                secret,
                payload_bytes,
                hashlib.sha256
            ).hexdigest()
            
            # Compara as assinaturas usando comparação segura contra timing attacks
            return hmac.compare_digest(calculated_hmac, signature)
        except Exception as e:
            logger.error(f"Erro ao verificar assinatura do webhook: {e}")
            return False
    
    @staticmethod
    def process_webhook(evento: str, payload: str, signature: Optional[str] = None) -> Webhook:
        """
        Processa um webhook recebido, verificando sua assinatura e salvando-o no banco de dados.
        
        Args:
            evento: O tipo de evento do webhook.
            payload: O payload do webhook em formato de string.
            signature: A assinatura do webhook fornecida pelo remetente (opcional).
            
        Returns:
            Webhook: O objeto Webhook criado.
        """
        verificado = False
        if signature:
            verificado = WebhookProcessor.verify_webhook(payload, signature)
        
        # Salva o webhook no banco de dados
        webhook = Webhook.objects.create(
            evento=evento,
            payload=payload,
            assinatura=signature,
            verificado=verificado
        )
        
        logger.info(
            f"Webhook recebido - ID: {webhook.id}, Evento: {evento}, "
            f"Verificado: {verificado}"
        )
        
        return webhook


class WebhookSender:
    """
    Classe responsável pelo envio de webhooks para endpoints externos.
    """
    
    @staticmethod
    def send_webhook(
        pedido_id: int, 
        status: str, 
        payload_data: Dict[str, Any],
        endpoint_config: Optional[WebhookEndpointConfig] = None
    ) -> Tuple[bool, int, str, WebhookStatusEnviado]:
        """
        Envia um webhook para o endpoint configurado.
        
        Args:
            pedido_id: ID do pedido relacionado.
            status: Status do pedido.
            payload_data: Dados a serem enviados no webhook.
            endpoint_config: Configuração do endpoint (opcional).
            
        Returns:
            Tuple[bool, int, str, WebhookStatusEnviado]: 
                - Sucesso do envio (bool)
                - Código HTTP (int)
                - Resposta (str)
                - Objeto WebhookStatusEnviado criado
        """
        if endpoint_config is None:
            endpoints = WebhookEndpointConfig.objects.filter(ativo=True, auto_enviar=True)
            if not endpoints.exists():
                logger.warning("Nenhuma configuração de endpoint ativa encontrada para envio automático")
                return False, 0, "Nenhum endpoint configurado", None
                
            # Usa o primeiro endpoint ativo encontrado
            endpoint_config = endpoints.first()
        
        # Prepara o payload
        payload = json.dumps(payload_data)
        url = endpoint_config.get_url_with_token()
        headers = endpoint_config.get_headers()
        
        # Cria o registro de status antes de enviar
        webhook_status = WebhookStatusEnviado.objects.create(
            pedido_id=pedido_id,
            status=status,
            url_destino=url,
            payload=payload,
            sucesso=False
        )
        
        try:
            # Envia o webhook
            response = requests.post(
                url=url,
                headers=headers,
                data=payload,
                timeout=10  # timeout em segundos
            )
            
            # Atualiza o registro com a resposta
            webhook_status.resposta = response.text
            webhook_status.codigo_http = response.status_code
            webhook_status.sucesso = 200 <= response.status_code < 300
            webhook_status.save()
            
            logger.info(
                f"Webhook enviado - Pedido: {pedido_id}, Status: {status}, "
                f"URL: {url}, HTTP: {response.status_code}, "
                f"Sucesso: {webhook_status.sucesso}"
            )
            
            return webhook_status.sucesso, response.status_code, response.text, webhook_status
            
        except Exception as e:
            # Atualiza o registro com o erro
            error_message = str(e)
            webhook_status.resposta = error_message
            webhook_status.sucesso = False
            webhook_status.save()
            
            logger.error(
                f"Erro ao enviar webhook - Pedido: {pedido_id}, "
                f"Status: {status}, URL: {url}, Erro: {error_message}"
            )
            
            return False, 0, error_message, webhook_status
