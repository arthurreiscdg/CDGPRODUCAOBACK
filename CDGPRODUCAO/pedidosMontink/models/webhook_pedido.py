from django.db import models

class Pedido(models.Model):
    # Dados do pedido
    titulo = models.CharField(max_length=255)
    valor_pedido = models.DecimalField(max_digits=10, decimal_places=2)
    custo_envio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    etiqueta_envio = models.URLField(null=True, blank=True)
    metodo_envio = models.IntegerField(null=True, blank=True)
    numero_pedido = models.IntegerField(unique=True)
    nome_cliente = models.CharField(max_length=255)
    documento_cliente = models.CharField(max_length=20)
    email_cliente = models.EmailField()
    pdf_path = models.CharField(max_length=255, null=True, blank=True)

    # Status e webhook (supondo que StatusPedido e Webhook ainda existem em outra parte do sistema)
    status = models.ForeignKey('StatusPedido', on_delete=models.PROTECT, related_name='pedidos')
    webhook = models.ForeignKey('Webhook', on_delete=models.CASCADE, related_name='pedidos')

    # Endereço de envio (endereço completo dentro da tabela Pedido)
    nome_destinatario = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    cep = models.CharField(max_length=9)
    bairro = models.CharField(max_length=100)
    telefone_destinatario = models.CharField(max_length=20)
    pais = models.CharField(max_length=50)

    # Informações adicionais
    nome_info_adicional = models.CharField(max_length=255)
    telefone_info_adicional = models.CharField(max_length=20)
    email_info_adicional = models.EmailField()

    # Dados do produto (limitado a 1 produto por pedido – necessário se for uma única tabela)
    nome_produto = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    quantidade = models.IntegerField()
    id_sku = models.IntegerField(null=True, blank=True)
    arquivo_pdf_produto = models.URLField(null=True, blank=True)

    # Design
    design_capa_frente = models.URLField()
    design_capa_verso = models.URLField(blank=True, null=True)

    # Mockup
    mockup_capa_frente = models.URLField()
    mockup_capa_costas = models.URLField(blank=True, null=True)

    # Timestamps
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.nome_cliente}"

    class Meta:
        db_table = 'pedidos'  # define o nome fixo da tabela
        ordering = ['-criado_em']


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