from django.db import models
from django.utils import timezone
from django.conf import settings

class Unidade(models.Model):
    """
    Modelo para armazenar as unidades relacionadas a um formulário.
    Cada unidade pode ter uma quantidade específica.
    """
    # Choices para nomes das unidades
    NOME_CHOICES = [
        ('ARARUAMA', 'Araruama'),
        ('CABO_FRIO', 'Cabo Frio'),
        ('ITABORAI', 'Itaboraí'),
        ('ITAIPUACU', 'Itaipuaçu'),
        ('MARICA_I', 'Maricá I'),
        ('NOVA_FRIBURGO', 'Nova Friburgo'),
        ('QUEIMADOS', 'Queimados'),
        ('SEROPEDICA', 'Seropédica'),
        ('ALCANTARA', 'Alcântara'),
        ('BANGU', 'Bangu'),
        ('BARRA_DA_TIJUCA', 'Barra da Tijuca'),
        ('BELFORD_ROXO', 'Belford Roxo'),
        ('DUQUE_DE_CAXIAS', 'Duque de Caxias'),
        ('ICARAI', 'Icaraí'),
        ('ILHA_DO_GOVERNADOR', 'Ilha do Governador'),
        ('ITAIPU', 'Itaipu'),
        ('MADUREIRA', 'Madureira'),
        ('MEIER', 'Méier'),
        ('NILOPOLIS', 'Nilópolis'),
        ('NITEROI', 'Niterói'),
        ('NOVA_IGUACU', 'Nova Iguaçu'),
        ('OLARIA', 'Olaria'),
        ('PRATA', 'Prata'),
        ('SAO_GONCALO', 'São Gonçalo'),
        ('SAO_JOAO_DE_MERITI', 'São João de Meriti'),
        ('VILA_ISABEL', 'Vila Isabel'),
        ('VILAR_DOS_TELES', 'Vilar dos Teles'),
    ]
    
    # Relação com o formulário
    formulario = models.ForeignKey(
        'formsProducao.Formulario', 
        on_delete=models.CASCADE,
        related_name='unidades',
        verbose_name="Formulário"
    )
      # Campos da unidade
    nome = models.CharField(max_length=100, choices=NOME_CHOICES, verbose_name="Nome da Unidade")
    quantidade = models.IntegerField(default=1, verbose_name="Quantidade")
    
    # Campos de controle temporal
    criado_em = models.DateTimeField(default=timezone.now)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Unidade"
        verbose_name_plural = "Unidades"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.quantidade} unidade(s)"
