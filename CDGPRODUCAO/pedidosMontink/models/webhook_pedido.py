from django.db import models


class Pedido(models.Model):
    titulo = models.CharField(max_length=255)
    valor_pedido = models.DecimalField(max_digits=10, decimal_places=2)
    custo_envio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    etiqueta_envio = models.URLField(null=True, blank=True)
    metodo_envio = models.IntegerField(null=True, blank=True)
    numero_pedido = models.IntegerField(unique=True)
    nome_cliente = models.CharField(max_length=255)
    documento_cliente = models.CharField(max_length=20)
    email_cliente = models.EmailField()
    status = models.ForeignKey(StatusPedido, on_delete=models.PROTECT, related_name='pedidos')
    pdf_path = models.CharField(max_length=255, null=True, blank=True)
    
    # Relacionamentos
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='pedidos')
    endereco_envio = models.OneToOneField(EnderecoEnvio, on_delete=models.CASCADE)
    informacoes_adicionais = models.OneToOneField(InformacoesAdicionais, on_delete=models.CASCADE)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.nome_cliente}"

    class Meta:
        ordering = ['-criado_em']

class InformacoesAdicionais(models.Model):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.nome
    
class Produto(models.Model):
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    quantidade = models.IntegerField()
    id_sku = models.IntegerField(null=True, blank=True)
    designs = models.OneToOneField(Design, on_delete=models.CASCADE)
    mockups = models.OneToOneField(Mockup, on_delete=models.CASCADE)
    arquivo_pdf = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.nome} - {self.sku}"
    

class EnderecoEnvio(models.Model):
    nome_destinatario = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    cep = models.CharField(max_length=9)
    bairro = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    pais = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nome_destinatario} - {self.cidade}/{self.uf}"

class Design(models.Model):
    capa_frente = models.URLField()
    capa_verso = models.URLField(blank=True, null=True)

    def __str__(self):
        return "Design"

class Mockup(models.Model):
    capa_frente = models.URLField()
    capa_costas = models.URLField(blank=True, null=True)

    def __str__(self):
        return "Mockup"