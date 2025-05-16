from django.db import models
from .webhook_pedido import Pedido


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