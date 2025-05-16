from django.db import models

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