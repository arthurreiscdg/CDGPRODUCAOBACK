import json
import hmac
import hashlib
import requests
from django.conf import settings
from ..models import Webhook, WebhookConfig, WebhookStatusEnviado, WebhookEndpointConfig, Pedido, StatusPedido


class WebhookService:
    """
    Serviço de gerenciamento de webhooks.
    Implementa a lógica de verificação de assinatura, processamento e envio de webhooks.
    """
    @staticmethod
    def verificar_assinatura(payload, assinatura, secret_key=None):
        """
        Verifica a assinatura de um webhook usando HMAC-SHA256.
        
        Args:
            payload (str): Payload do webhook em formato JSON
            assinatura (str): Assinatura fornecida pelo remetente
            secret_key (str, opcional): Chave secreta para verificação. Se não fornecida,
                                       usa a chave configurada nas configurações.
                                       
        Returns:
            tuple: (bool, WebhookConfig) - True se a assinatura for válida, False caso contrário,
                                          e a configuração de webhook utilizada (se existir)
        """
        webhook_config = None
        if not secret_key:
            try:
                webhook_config = WebhookConfig.objects.filter(ativo=True).first()
                if webhook_config:
                    secret_key = webhook_config.secret_key
                else:
                    # Fallback para a chave nas configurações
                    secret_key = settings.WEBHOOK_SECRET_KEY
            except (WebhookConfig.DoesNotExist, AttributeError):
                secret_key = settings.WEBHOOK_SECRET_KEY
        
        if not secret_key or not assinatura:
            return False, webhook_config
        
        # Calcula o hash HMAC-SHA256 do payload
        calculado = hmac.new(
            secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256        ).hexdigest()
        
        # Compara com a assinatura fornecida
        return hmac.compare_digest(calculado, assinatura), webhook_config
        
    @classmethod
    def processar_webhook(cls, payload, assinatura=None, evento='pedido'):
        """
        Processa um webhook recebido, verifica a assinatura e salva os dados.
        
        Args:
            payload (str): Payload do webhook em formato JSON
            assinatura (str, opcional): Assinatura fornecida pelo remetente
            evento (str): Tipo de evento do webhook
            
        Returns:
            tuple: (Webhook, Pedido, bool) - Instância do Webhook, instância do Pedido criado (se houver) e status de verificação
        """
        # Cria o registro do webhook
        webhook = Webhook.objects.create(
            evento=evento,
            payload=payload,
            assinatura=assinatura,
            verificado=False
        )
        
        # Verifica a assinatura se fornecida
        verificado = False
        webhook_config = None
        if assinatura:
            verificado, webhook_config = cls.verificar_assinatura(payload, assinatura)
            webhook.verificado = verificado
            webhook.save(update_fields=['verificado'])
        
        # Se a assinatura for válida ou não for obrigatória, processa o webhook
        pedido = None
        if verificado or not assinatura:
            data = json.loads(payload)
            pedido = cls.criar_pedido_de_webhook(data, webhook)
        
        return webhook, pedido, verificado
    @staticmethod
    def criar_pedido_de_webhook(data, webhook):
        """
        Cria um novo pedido a partir dos dados do webhook.
        
        Args:
            data (dict): Dados do pedido recebidos no webhook
            webhook (Webhook): Instância do webhook associado
            
        Returns:
            Pedido: Instância do pedido criado
        """
        # Obtém o status padrão (ou cria se não existir)
        status_padrao, _ = StatusPedido.objects.get_or_create(
            nome="Recebido", 
            defaults={
                'descricao': 'Pedido recebido e aguardando processamento',
                'ordem': 1
            }
        )
        
        # Coleta dados do primeiro produto (modelo atual suporta apenas um produto por pedido)
        produto = data.get('produtos', [])[0] if data.get('produtos') else {}
        
        # Cria o pedido
        pedido = Pedido.objects.create(
            # Dados do pedido
            titulo=f"Pedido #{data.get('numero_pedido')}",
            valor_pedido=data.get('valor_pedido', 0),
            custo_envio=data.get('custo_envio'),
            etiqueta_envio=data.get('etiqueta_envio'),
            metodo_envio=data.get('metodo_envio'),
            numero_pedido=data.get('numero_pedido'),
            nome_cliente=data.get('nome_cliente', ''),
            documento_cliente=data.get('documento_cliente', ''),
            email_cliente=data.get('email_cliente', ''),
            
            # Status e webhook
            status=status_padrao,
            webhook=webhook,
            
            # Endereço
            nome_destinatario=data.get('endereco_envio', {}).get('nome_destinatario', ''),
            endereco=data.get('endereco_envio', {}).get('endereco', ''),
            numero=data.get('endereco_envio', {}).get('numero', ''),
            complemento=data.get('endereco_envio', {}).get('complemento'),
            cidade=data.get('endereco_envio', {}).get('cidade', ''),
            uf=data.get('endereco_envio', {}).get('uf', ''),
            cep=data.get('endereco_envio', {}).get('cep', ''),
            bairro=data.get('endereco_envio', {}).get('bairro', ''),
            telefone_destinatario=data.get('endereco_envio', {}).get('telefone', ''),
            pais=data.get('endereco_envio', {}).get('pais', 'Brasil'),
            
            # Informações adicionais
            nome_info_adicional=data.get('informacoes_adicionais', {}).get('nome', ''),
            telefone_info_adicional=data.get('informacoes_adicionais', {}).get('telefone', ''),
            email_info_adicional=data.get('informacoes_adicionais', {}).get('email', ''),
            
            # Dados do produto
            nome_produto=produto.get('nome', ''),
            sku=produto.get('sku', ''),
            quantidade=produto.get('quantidade', 0),
            id_sku=produto.get('id_sku'),
            arquivo_pdf_produto=produto.get('arquivo_pdf'),
            
            # Design
            design_capa_frente=produto.get('designs', {}).get('capa_frente', ''),
            design_capa_verso=produto.get('designs', {}).get('capa_verso', ''),
            
            # Mockup
            mockup_capa_frente=produto.get('mockups', {}).get('capa_frente', ''),
            mockup_capa_costas=produto.get('mockups', {}).get('capa_costas', '')
        )
        
        return pedido

    @classmethod
    def enviar_webhook_status(cls, pedido, status=None):
        """
        Envia webhooks de status para os endpoints configurados.
        
        Args:
            pedido (Pedido): Pedido cujo status será enviado
            status (str, opcional): Status a enviar (se None, usa o status atual do pedido)
            
        Returns:
            list: Lista de instâncias de WebhookStatusEnviado criadas
        """
        # Se o status não for especificado, usa o status atual do pedido
        if status is None and pedido.status:
            status = pedido.status.nome
        elif status is None:
            return []
        
        # Obtém todos os endpoints ativos configurados para envio automático
        endpoints = WebhookEndpointConfig.objects.filter(ativo=True, auto_enviar=True)
        resultados = []
        
        # Cria o payload do webhook
        payload = cls._criar_payload_status(pedido, status)
        
        # Envia para cada endpoint
        for endpoint in endpoints:
            resultado = cls._enviar_para_endpoint(pedido, status, endpoint, payload)
            resultados.append(resultado)
        
        return resultados
    
    @staticmethod
    def _criar_payload_status(pedido, status):
        """
        Cria o payload para envio de status.
        
        Args:
            pedido (Pedido): Pedido cujas informações serão incluídas no payload
            status (str): Status a ser enviado
            
        Returns:
            dict: Payload formatado
        """
        return {
            'numero_pedido': pedido.numero_pedido,
            'status': status,
            'timestamp': pedido.atualizado_em.isoformat() if pedido.atualizado_em else None,
            'detalhes': {
                'id': pedido.id,
                'nome_cliente': pedido.nome_cliente,
                'valor_pedido': float(pedido.valor_pedido),
                'produtos': [{
                    'nome': pedido.nome_produto,
                    'sku': pedido.sku,
                    'quantidade': pedido.quantidade
                }]
            }
        }
    
    @staticmethod
    def _enviar_para_endpoint(pedido, status, endpoint, payload):
        """
        Envia o webhook para um endpoint específico.
        
        Args:
            pedido (Pedido): Pedido associado
            status (str): Status a ser enviado
            endpoint (WebhookEndpointConfig): Configuração do endpoint
            payload (dict): Payload a ser enviado
            
        Returns:
            WebhookStatusEnviado: Registro do webhook enviado
        """
        # Registra a tentativa antes de enviar
        webhook_enviado = WebhookStatusEnviado.objects.create(
            pedido=pedido,
            status=status,
            url_destino=endpoint.url,
            payload=json.dumps(payload),
            sucesso=False
        )
        
        # Preparar a URL (incorporando token se necessário)
        url = endpoint.url
        if endpoint.access_token:
            separator = '?' if '?' not in url else '&'
            url = f"{url}{separator}token={endpoint.access_token}"
        
        # Preparar headers
        headers = {'Content-Type': 'application/json'}
        if endpoint.token_autenticacao:
            headers['Authorization'] = f"Bearer {endpoint.token_autenticacao}"
        
        # Adicionar headers adicionais, se configurados
        if endpoint.headers_adicionais:
            try:
                headers_adicionais = json.loads(endpoint.headers_adicionais)
                if isinstance(headers_adicionais, dict):
                    headers.update(headers_adicionais)
            except json.JSONDecodeError:
                pass  # Ignora se os headers adicionais não forem JSON válido
        
        try:
            # Envia o webhook
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            # Atualiza o registro com a resposta
            webhook_enviado.resposta = response.text[:1000]  # Limita o tamanho da resposta
            webhook_enviado.codigo_http = response.status_code
            webhook_enviado.sucesso = 200 <= response.status_code < 300
            webhook_enviado.save()
        
        except Exception as e:
            # Em caso de erro, registra a exceção
            webhook_enviado.resposta = str(e)[:1000]
            webhook_enviado.save()
        
        return webhook_enviado
