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
                
                # No novo formato, o evento pode não estar presente
                if not evento and 'produtos' in payload:
                    evento = 'pedido.novo'  # Assumir um evento padrão se não for fornecido
                    
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
                # Atualizar o webhook com informações de erro
                webhook.status_code = 401  # Unauthorized
                webhook.erro = "Assinatura inválida"
                webhook.processado = False
                webhook.save()
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
                # O modelo de JSON novo já está no formato adequado, sem o objeto pedido dentro
                dados_pedido = payload
                if not dados_pedido:
                    return False, "Dados do pedido não encontrados no payload", None
                
                # Verificar se o número do pedido já existe
                numero_pedido = dados_pedido.get('numero_pedido')
                if not numero_pedido:
                    return False, "Número do pedido não fornecido", None
                
                pedido_existente = Pedido.objects.filter(numero_pedido=numero_pedido).first()
                if pedido_existente:
                    return False, f"Pedido com número {numero_pedido} já existe", None
                
                # Informações adicionais agora vem em um objeto separado
                info_adicional = dados_pedido.get('informacoes_adicionais', {})
                
                # Endereço de envio agora vem em um objeto separado
                endereco_envio = dados_pedido.get('endereco_envio', {})
                
                # Produtos agora vêm em uma lista (array)
                produtos = dados_pedido.get('produtos', [])
                if not produtos:
                    return False, "Nenhum produto especificado no pedido", None
                
                # Pegar o primeiro produto (como no modelo atual só suporta um produto)
                primeiro_produto = produtos[0]
                
                # Extrair designs e mockups do primeiro produto
                designs = primeiro_produto.get('designs', {})
                mockups = primeiro_produto.get('mockups', {})
                
                # Criar o pedido
                try:
                    titulo = f"Pedido #{numero_pedido}"
                    if primeiro_produto.get('nome'):
                        titulo = f"{titulo} - {primeiro_produto.get('nome')}"
                        
                    pedido = Pedido(
                        # Dados básicos do pedido
                        numero_pedido=numero_pedido,
                        titulo=titulo,
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
                        
                        # Endereço - agora vem do objeto endereco_envio
                        nome_destinatario=endereco_envio.get('nome_destinatario', ''),
                        endereco=endereco_envio.get('endereco', ''),
                        numero=endereco_envio.get('numero', ''),
                        complemento=endereco_envio.get('complemento'),
                        cidade=endereco_envio.get('cidade', ''),
                        uf=endereco_envio.get('uf', ''),
                        cep=endereco_envio.get('cep', ''),
                        bairro=endereco_envio.get('bairro', ''),
                        telefone_destinatario=endereco_envio.get('telefone', ''),
                        pais=endereco_envio.get('pais', 'Brasil'),
                        
                        # Informações adicionais - agora vem do objeto informacoes_adicionais
                        nome_info_adicional=info_adicional.get('nome', ''),
                        telefone_info_adicional=info_adicional.get('telefone', ''),
                        email_info_adicional=info_adicional.get('email', ''),
                        
                        # Produto - vem do primeiro produto da lista de produtos
                        nome_produto=primeiro_produto.get('nome', ''),
                        sku=primeiro_produto.get('sku', ''),
                        quantidade=primeiro_produto.get('quantidade', 1),
                        id_sku=primeiro_produto.get('id_sku'),
                        arquivo_pdf_produto=primeiro_produto.get('arquivo_pdf'),
                        
                        # Design - agora vem do objeto designs dentro do produto
                        design_capa_frente=designs.get('capa_frente', ''),
                        design_capa_verso=designs.get('capa_verso'),
                        
                        # Mockup - agora vem do objeto mockups dentro do produto
                        mockup_capa_frente=mockups.get('capa_frente', ''),
                        mockup_capa_costas=mockups.get('capa_costas')
                    )
                    pedido.save()
                      # Atualizar o webhook com informações de sucesso
                    webhook.status_code = 201  # Created
                    webhook.processado = True
                    webhook.save()
                    
                    return True, f"Pedido #{numero_pedido} recebido com sucesso", pedido.id
                
                except Exception as e:
                    # Rollback é automático devido ao uso de transaction.atomic()
                    erro_msg = f"Erro ao salvar o pedido: {str(e)}"
                    
                    # Atualizar o webhook com informações de erro
                    webhook.status_code = 500  # Internal Server Error
                    webhook.erro = erro_msg
                    webhook.processado = False
                    webhook.save()
                    
                    return False, erro_msg, None
        
        except Exception as e:
            erro_msg = f"Erro ao processar webhook: {str(e)}"
            
            # Se o webhook já foi criado, atualizá-lo com informações de erro
            try:
                if 'webhook' in locals():
                    webhook.status_code = 500  # Internal Server Error
                    webhook.erro = erro_msg
                    webhook.processado = False
                    webhook.save()
            except:
                pass  # Se não conseguir atualizar o webhook, apenas continue
                
            return False, erro_msg, None