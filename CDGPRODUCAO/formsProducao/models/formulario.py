from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Formulario(models.Model):
    # Choices para formatos, cores e tipos de impressão
    FORMATO_CHOICES = [
        ('A4', 'A4'),
        ('A5', 'A5'),
        ('A3', 'A3'),
        ('CARTA', 'Carta'),
        ('OFICIO', 'Ofício'),
        ('OUTRO', 'Outro')
    ]
    
    COR_IMPRESSAO_CHOICES = [
        ('PB', 'Preto e Branco'),
        ('COLOR', 'Colorido')
    ]
    
    IMPRESSAO_CHOICES = [
        ('1_LADO', 'Um lado'),
        ('2_LADOS', 'Frente e verso'),
        ('LIVRETO', 'Livreto')
    ]    # Relação com o usuário que enviou o formulário
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,  # Se o usuário for excluído, mantém o formulário
        related_name='formularios',
        null=True,
        blank=True,
        verbose_name="Usuário que enviou"
    )
    
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
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES, default='A4', null=True, blank=True)
    cor_impressao = models.CharField(max_length=10, choices=COR_IMPRESSAO_CHOICES, default='PB', null=True, blank=True)
    impressao = models.CharField(max_length=20, choices=IMPRESSAO_CHOICES, default='1_LADO', null=True, blank=True)
      # Campos de ArquivoPDF
    arquivo = models.FileField(upload_to='pdfs/', null=True, blank=True)
    cod_op = models.CharField(max_length=10, null=True, blank=True)
    link_download = models.URLField(max_length=500, null=True, blank=True)
    web_view_link = models.URLField(max_length=500, null=True, blank=True, verbose_name="Link de visualização")
    json_link = models.URLField(max_length=500, null=True, blank=True)    # Campos de controle temporal
    criado_em = models.DateTimeField(default=timezone.now)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Formulário"
        verbose_name_plural = "Formulários"
        ordering = ['-criado_em']
        
    def __str__(self):
        return f"Formulário {self.id} - {self.titulo or 'Sem título'} ({self.nome or 'Anônimo'})"
