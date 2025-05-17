from django.db import models
from .webhook_pedido import Pedido

class WebhookEndpointConfig(models.Model):
    """
    Configuração para endpoints externos que receberão webhooks de status.
    
    Este modelo permite configurar URLs para onde os webhooks de status serão enviados
    automaticamente quando o status de um pedido for alterado.
    """
    nome = models.CharField(max_length=100, help_text="Nome para identificar este endpoint")
    url = models.URLField(help_text="URL para onde os webhooks serão enviados")
    ativo = models.BooleanField(default=True, help_text="Se desativado, webhooks não serão enviados para este endpoint")
    auto_enviar = models.BooleanField(default=True, help_text="Se ativado, webhooks serão enviados automaticamente")
    access_token = models.CharField(
        max_length=255, blank=True, null=True, 
        help_text="Token de autenticação opcional para incluir na URL"
    )
    token_autenticacao = models.CharField(
        max_length=255, blank=True, null=True, 
        help_text="Token de autenticação opcional para incluir nos cabeçalhos de requisição"
    )
    headers_adicionais = models.TextField(
        blank=True, null=True, 
        help_text="Cabeçalhos adicionais em formato JSON (por exemplo: {'X-Custom': 'Value'})"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nome} - {'Ativo' if self.ativo else 'Inativo'}"
    
    class Meta:
        verbose_name = "Configuração de Endpoint de Webhook"
        verbose_name_plural = "Configurações de Endpoints de Webhook"
        ordering = ['nome']


class WebhookConfig(models.Model):
    secret_key = models.CharField(max_length=255)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Webhook Config - {'Ativo' if self.ativo else 'Inativo'}"
    


class Webhook(models.Model):
    evento = models.CharField(max_length=50)
    payload = models.TextField()
    assinatura = models.CharField(max_length=255, null=True)
    verificado = models.BooleanField(default=False)
    recebido_em = models.DateTimeField(auto_now_add=True)
    status_code = models.IntegerField(null=True, blank=True, help_text="Código de status HTTP do processamento")
    erro = models.TextField(null=True, blank=True, help_text="Mensagem de erro, se houver")
    processado = models.BooleanField(default=False, help_text="Indica se o webhook foi processado com sucesso")

    def __str__(self):
        if self.status_code:
            return f"Webhook - {self.evento} - Status: {self.status_code} {'(Verificado)' if self.verificado else '(Não Verificado)'}"
        return f"Webhook - {self.evento} {'(Verificado)' if self.verificado else '(Não Verificado)'}"



class WebhookStatusEnviado(models.Model):
    """
    Registra os webhooks de status enviados para sistemas externos.
    
    Este modelo armazena informações sobre os webhooks de status que o sistema
    envia para sistemas externos, como por exemplo, para notificar sobre 
    atualizações no status de um pedido.
    """
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='webhooks_enviados')
    status = models.CharField(max_length=50)
    url_destino = models.URLField()
    payload = models.TextField()
    resposta = models.TextField(null=True, blank=True)
    codigo_http = models.IntegerField(null=True, blank=True)
    sucesso = models.BooleanField(default=False)
    enviado_em = models.DateTimeField(auto_now_add=True)
    tentativa_numero = models.IntegerField(default=1)
    
    def __str__(self):
        return f"Status webhook para pedido #{self.pedido.numero_pedido} - {'Sucesso' if self.sucesso else 'Falha'}"
    
    class Meta:
        ordering = ['-enviado_em']
        verbose_name = "Webhook de Status Enviado"
        verbose_name_plural = "Webhooks de Status Enviados"