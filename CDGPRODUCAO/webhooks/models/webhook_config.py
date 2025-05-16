from django.db import models

class WebhookConfig(models.Model):
    """
    Configuração de webhooks para receber notificações externas.
    
    Este modelo armazena configurações como chaves secretas para verificação
    de assinaturas de webhooks recebidos.
    """
    secret_key = models.CharField(max_length=255, help_text="Chave secreta para validação de assinaturas de webhooks")
    ativo = models.BooleanField(default=True, help_text="Indica se a configuração está ativa")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Webhook Config - {'Ativo' if self.ativo else 'Inativo'}"
    
    class Meta:
        verbose_name = "Configuração de Webhook"
        verbose_name_plural = "Configurações de Webhook"