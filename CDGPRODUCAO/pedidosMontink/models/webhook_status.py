from django.db import models


class StatusPedido(models.Model):
    """
    Modelo para armazenar os diferentes status que um pedido pode ter.
    
    Este modelo representa os possíveis estados de um pedido durante seu ciclo de vida,
    desde a criação até a entrega ou cancelamento.
    """
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True, null=True)
    cor_css = models.CharField(max_length=50, blank=True, null=True)
    ordem = models.IntegerField(default=0)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Status de Pedido"
        verbose_name_plural = "Status de Pedidos"
        ordering = ['ordem']