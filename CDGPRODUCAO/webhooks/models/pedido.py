from django.db import models
import json


class Pedido(models.Model):
    """
    Modelo para armazenar os pedidos recebidos via webhook.
    
    Este modelo armazena todas as informações do pedido em um único registro,
    com os dados de produtos, endereço e informações adicionais como JSON.
    """
    # Campos básicos do pedido
    webhook_id = models.IntegerField(null=True, blank=True, help_text="ID do webhook que originou este pedido")
    valor_pedido = models.DecimalField(max_digits=10, decimal_places=2)
    custo_envio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    etiqueta_envio = models.URLField(null=True, blank=True)
    metodo_envio = models.IntegerField(null=True, blank=True)
    numero_pedido = models.IntegerField(unique=True)
    nome_cliente = models.CharField(max_length=255)
    documento_cliente = models.CharField(max_length=20)
    email_cliente = models.EmailField()
    
    # Campos JSON para dados relacionados
    produtos_json = models.TextField(help_text="Lista de produtos em formato JSON")
    endereco_envio_json = models.TextField(help_text="Dados de endereço de envio em formato JSON")
    informacoes_adicionais_json = models.TextField(help_text="Informações adicionais em formato JSON")
    
    # Campos para controle de status
    status = models.CharField(max_length=50, default="recebido", help_text="Status atual do pedido")
    
    # Campos para controle de datas
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.nome_cliente}"
    
    @property
    def produtos(self):
        """Retorna os produtos como um objeto Python."""
        try:
            return json.loads(self.produtos_json)
        except Exception:
            return []
    
    @property
    def endereco_envio(self):
        """Retorna o endereço de envio como um objeto Python."""
        try:
            return json.loads(self.endereco_envio_json)
        except Exception:
            return {}
    
    @property
    def informacoes_adicionais(self):
        """Retorna as informações adicionais como um objeto Python."""
        try:
            return json.loads(self.informacoes_adicionais_json)
        except Exception:
            return {}
    
    @classmethod
    def criar_do_webhook(cls, webhook):
        """
        Cria um novo pedido a partir de um webhook recebido.
        
        Args:
            webhook: Objeto Webhook com o payload recebido
            
        Returns:
            Pedido: Nova instância de Pedido salva no banco de dados
        """
        try:
            # Carrega o payload do webhook como JSON
            dados = json.loads(webhook.payload)
            
            # Cria o pedido com os dados básicos
            pedido = cls(
                webhook_id=webhook.id,
                valor_pedido=dados.get('valor_pedido', 0),
                custo_envio=dados.get('custo_envio'),
                etiqueta_envio=dados.get('etiqueta_envio'),
                metodo_envio=dados.get('metodo_envio'),
                numero_pedido=dados.get('numero_pedido'),
                nome_cliente=dados.get('nome_cliente', ''),
                documento_cliente=dados.get('documento_cliente', ''),
                email_cliente=dados.get('email_cliente', ''),
                produtos_json=json.dumps(dados.get('produtos', [])),
                endereco_envio_json=json.dumps(dados.get('endereco_envio', {})),
                informacoes_adicionais_json=json.dumps(dados.get('informacoes_adicionais', {}))
            )
            
            # Salva o pedido no banco de dados
            pedido.save()
            return pedido
        
        except Exception as e:
            raise ValueError(f"Erro ao criar pedido a partir do webhook: {str(e)}")
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-criado_em']
