from django.db import models

class WebhookStatusEnviado(models.Model):
    """
    Registra os webhooks de status enviados para sistemas externos.
    
    Este modelo armazena informações sobre os webhooks de status que o sistema
    envia para sistemas externos, como por exemplo, para notificar sobre 
    atualizações no status de um pedido.
    """
    pedido_id = models.IntegerField(help_text="ID do pedido relacionado a este webhook")
    status = models.CharField(max_length=50, help_text="Status do pedido que gerou o webhook")
    url_destino = models.URLField(help_text="URL para onde o webhook foi enviado")
    payload = models.TextField(help_text="Conteúdo enviado no webhook")
    resposta = models.TextField(null=True, blank=True, help_text="Resposta recebida do endpoint")
    codigo_http = models.IntegerField(null=True, blank=True, help_text="Código HTTP da resposta")
    sucesso = models.BooleanField(default=False, help_text="Indica se o envio foi bem-sucedido")
    enviado_em = models.DateTimeField(auto_now_add=True)
    tentativa_numero = models.IntegerField(default=1, help_text="Número da tentativa de envio")
    
    def __str__(self):
        return f"Status webhook para pedido #{self.pedido_id} - {'Sucesso' if self.sucesso else 'Falha'}"
    
    class Meta:
        ordering = ['-enviado_em']
        verbose_name = "Webhook de Status Enviado"
        verbose_name_plural = "Webhooks de Status Enviados"