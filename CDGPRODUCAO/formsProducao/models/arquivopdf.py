from django.db import models
from django.utils import timezone

class ArquivoPDF(models.Model):
    """
    Modelo para armazenar arquivos PDF associados a um formulário.
    Permite que um formulário tenha múltiplos arquivos PDF.
    """
    # Relação com o formulário
    formulario = models.ForeignKey(
        'formsProducao.Formulario',
        on_delete=models.CASCADE,
        related_name='arquivos_pdf',
        verbose_name="Formulário"
    )
    
    # Campos de arquivo
    nome = models.CharField(max_length=255, verbose_name="Nome do arquivo")
    arquivo = models.FileField(upload_to='pdfs/', null=True, blank=True)
    link_download = models.URLField(max_length=500, null=True, blank=True)
    web_view_link = models.URLField(max_length=500, null=True, blank=True, verbose_name="Link de visualização")
    json_link = models.URLField(max_length=500, null=True, blank=True)
    
    # Campos de controle temporal
    criado_em = models.DateTimeField(default=timezone.now)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Arquivo PDF"
        verbose_name_plural = "Arquivos PDF"
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"PDF {self.id} - {self.nome} (Formulário {self.formulario.cod_op})"