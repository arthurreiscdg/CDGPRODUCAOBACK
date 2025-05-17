from django.db import models
class Formulario(models.Model):
    # Campos de Contato
    nome = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    # Campos de Unidade
    unidade_nome = models.CharField(max_length=50, null=True, blank=True)
    unidade_quantidade = models.IntegerField(null=True, blank=True)
    
    # Campos de Configuração de Impressão
    titulo = models.CharField(max_length=255, null=True, blank=True)
    data_entrega = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    formato = models.CharField(max_length=10, choices=[...], default='A4', null=True, blank=True)
    cor_impressao = models.CharField(max_length=10, choices=[...], default='PB', null=True, blank=True)
    impressao = models.CharField(max_length=20, choices=[...], default='1_LADO', null=True, blank=True)
    # outros campos da configuração...

    # Campos de ArquivoPDF
    arquivo = models.FileField(upload_to='pdfs/', null=True, blank=True)
    cod_op = models.CharField(max_length=10, null=True, blank=True)
    link_download = models.URLField(max_length=500, null=True, blank=True)
    json_link = models.URLField(max_length=500, null=True, blank=True)

    criado_em = models.DateTimeField(default=timezone.now)
    atualizado_em = models.DateTimeField(auto_now=True)
