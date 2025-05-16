from django.db import models


class WebhookConfig(models.Model):
    secret_key = models.CharField(max_length=255)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Webhook Config - {'Ativo' if self.ativo else 'Inativo'}"