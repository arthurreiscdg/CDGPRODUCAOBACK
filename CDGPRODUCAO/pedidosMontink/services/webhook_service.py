import json
import hmac
import hashlib
from django.db import transaction
from django.conf import settings
from pedidosMontink.models import WebhookConfig, Webhook, Pedido, StatusPedido
from django.core.exceptions import ObjectDoesNotExist


class WebhookService:
    @staticmethod
    def verificar_assinatura(payload_raw, assinatura_recebida, secret_key):
        """
        Verifica se a assinatura do webhook é válida usando HMAC-SHA256.
        
        Args:
            payload_raw (bytes): O payload bruto do webhook
            assinatura_recebida (str): A assinatura recebida no header
            secret_key (str): A chave secreta para verificação
            
        Returns:
            bool: True se a assinatura for válida, False caso contrário
        """
        if not assinatura_recebida or not secret_key:
            return False
            
        assinatura_calculada = hmac.new(
            key=secret_key.encode(),
            msg=payload_raw,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(assinatura_calculada, assinatura_recebida)
    
    @staticmethod
    def processar_webhook_pedido(payload_raw, assinatura_recebida=None):
        """
        Processa um webhook recebido com dados de pedido.
        
        Args:
            payload_raw (bytes): O payload bruto do webhook
            assinatura_recebida (str): A assinatura recebida no header
            
        Returns:
            tuple: (sucesso, mensagem, pedido_id)
        """
        try:
            # Verificar se existe configuração de webhook ativa
            try:
                config = WebhookConfig.objects.filter(ativo=True).first()
                if not config:
                    return False, "Configuração de webhook não encontrada ou inativa", None
            except Exception as e:
                return False, f"Erro ao buscar configuração de webhook: {str(e)}", None
            
            # Converter o payload para JSON
            try:
                payload_str = payload_raw.decode('utf-8')
                payload = json.loads(payload_str)
                evento = payload.get('evento', 'pedido.novo')
            except json.JSONDecodeError:
                return False, "Payload inválido: não é um JSON válido", None
            
            # Verificar assinatura se fornecida
            assinatura_verificada = False
            if assinatura_recebida:
                assinatura_verificada = WebhookService.verificar_assinatura(
                    payload_raw, assinatura_recebida, config.secret_key
                )
            
            # Salvar o webhook recebido
            webhook = Webhook.objects.create(
                evento=evento,
                payload=payload_str,
                assinatura=assinatura_recebida,
                verificado=assinatura_verificada
            )
            
            # Se a assinatura foi fornecida mas é inválida, retornar erro
            if assinatura_recebida and not assinatura_verificada:
                return False, "Assinatura inválida", None
            
            # Processar os dados do pedido
            with transaction.atomic():
                # Buscar o status "Pedido Novo"
                try:
                    status_novo = StatusPedido.objects.get(nome="Pedido Novo")
                except StatusPedido.DoesNotExist:
                    # Criar o status se não existir
                    status_novo = StatusPedido.objects.create(
                        nome="Pedido Novo",
                        descricao="Pedido recém recebido via webhook",
                        cor_css="#3498db",
                        ordem=1
                    )
                
                # Extrair dados do pedido do payload
                dados_pedido = payload.get('pedido', {})
                if not dados_pedido:
                    return False, "Dados do pedido não encontrados no payload", None
                
                # Verificar se o número do pedido já existe
                numero_pedido = dados_pedido.get('numero_pedido')
                if not numero_pedido:
                    return False, "Número do pedido não fornecido", None
                
                pedido_existente = Pedido.objects.filter(numero_pedido=numero_pedido).first()
                if pedido_existente:
                    return False, f"Pedido com número {numero_pedido} já existe", None
                
                # Criar o pedido
                try:
                    pedido = Pedido(
                        # Dados básicos do pedido
                        numero_pedido=numero_pedido,
                        titulo=dados_pedido.get('titulo', f'Pedido #{numero_pedido}'),
                        valor_pedido=dados_pedido.get('valor_pedido', 0),
                        custo_envio=dados_pedido.get('custo_envio'),
                        etiqueta_envio=dados_pedido.get('etiqueta_envio'),
                        metodo_envio=dados_pedido.get('metodo_envio'),
                        
                        # Dados do cliente
                        nome_cliente=dados_pedido.get('nome_cliente', ''),
                        documento_cliente=dados_pedido.get('documento_cliente', ''),
                        email_cliente=dados_pedido.get('email_cliente', ''),
                        
                        # Status e webhook
                        status=status_novo,
                        webhook=webhook,
                        
                        # Endereço
                        nome_destinatario=dados_pedido.get('nome_destinatario', ''),
                        endereco=dados_pedido.get('endereco', ''),
                        numero=dados_pedido.get('numero', ''),
                        complemento=dados_pedido.get('complemento'),
                        cidade=dados_pedido.get('cidade', ''),
                        uf=dados_pedido.get('uf', ''),
                        cep=dados_pedido.get('cep', ''),
                        bairro=dados_pedido.get('bairro', ''),
                        telefone_destinatario=dados_pedido.get('telefone_destinatario', ''),
                        pais=dados_pedido.get('pais', 'Brasil'),
                        
                        # Informações adicionais
                        nome_info_adicional=dados_pedido.get('nome_info_adicional', ''),
                        telefone_info_adicional=dados_pedido.get('telefone_info_adicional', ''),
                        email_info_adicional=dados_pedido.get('email_info_adicional', ''),
                        
                        # Produto
                        nome_produto=dados_pedido.get('nome_produto', ''),
                        sku=dados_pedido.get('sku', ''),
                        quantidade=dados_pedido.get('quantidade', 1),
                        id_sku=dados_pedido.get('id_sku'),
                        arquivo_pdf_produto=dados_pedido.get('arquivo_pdf_produto'),
                        
                        # Design
                        design_capa_frente=dados_pedido.get('design_capa_frente', ''),
                        design_capa_verso=dados_pedido.get('design_capa_verso'),
                        
                        # Mockup
                        mockup_capa_frente=dados_pedido.get('mockup_capa_frente', ''),
                        mockup_capa_costas=dados_pedido.get('mockup_capa_costas')
                    )
                    pedido.save()
                    
                    return True, f"Pedido #{numero_pedido} recebido com sucesso", pedido.id
                
                except Exception as e:
                    # Rollback é automático devido ao uso de transaction.atomic()
                    return False, f"Erro ao salvar o pedido: {str(e)}", None
        
        except Exception as e:
            return False, f"Erro ao processar webhook: {str(e)}", None