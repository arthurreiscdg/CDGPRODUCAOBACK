from django.db import models


class Webhook(models.Model):
    evento = models.CharField(max_length=50)
    payload = models.TextField()
    assinatura = models.CharField(max_length=255, null=True)
    verificado = models.BooleanField(default=False)
    recebido_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Webhook - {self.evento} {'(Verificado)' if self.verificado else '(Não Verificado)'}"
