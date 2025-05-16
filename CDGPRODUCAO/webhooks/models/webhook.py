from django.db import models

class Webhook(models.Model):
    """
    Modelo para armazenar webhooks recebidos de sistemas externos.
    
    Este modelo registra os dados dos webhooks recebidos, incluindo o evento,
    payload, assinatura e status de verificação.
    """
    evento = models.CharField(max_length=50, help_text="Tipo de evento do webhook")
    payload = models.TextField(help_text="Conteúdo do payload recebido no webhook")
    assinatura = models.CharField(max_length=255, null=True, help_text="Assinatura para verificação")
    verificado = models.BooleanField(default=False, help_text="Indica se o webhook foi verificado com sucesso")
    recebido_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Webhook - {self.evento} {'(Verificado)' if self.verificado else '(Não Verificado)'}"
    
    class Meta:
        verbose_name = "Webhook Recebido"
        verbose_name_plural = "Webhooks Recebidos"
        ordering = ['-recebido_em']